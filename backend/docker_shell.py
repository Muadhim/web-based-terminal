import docker
import threading
import queue

client = docker.from_env()


class DockerShellSession:
    def __init__(self, username):
        self.username = username
        self.container = client.containers.run(
            "ubuntu:20.04",
            # command=f"/bin/bash -c \"useradd -m {username} && su - {username}\"",
            command="/bin/bash",
            stdin_open=True,
            tty=True,
            detach=True,
            remove=True,  # auto-delete on exit
            # network_mode="none",  # no internet
            # user="1000:1000", # do no user this for now  # non-root 
            # cap_drop=["ALL"],  # drop all linux capabilities
            # cap_add=["CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "FOWNER", "KILL"],
            # read_only=True, # prevent modification of the container FS
            tmpfs={"/tmp": "", "/home": ""},  # add writabe mounts for /temp, /home
            # limit resources
            mem_limit="128m",
            cpu_period=100000,
            cpu_quota=50000, # = 0.5 cpu core
            security_opt=["seccomp=unconfined"]  # Replace with your custom seccomp later

        )

        #attach to the container's stdin/stdout
        # self.sock = self.container.attach_socket(
        #     params={
        #         "stdin": 1,
        #         "stdout": 1,
        #         "stderr": 1,
        #         "stream":1,
        #         "logs":1
        #     }
        # )

        # start a shell inside the container using exec_run
        exec_instance = client.api.exec_create(
            self.container.id,
            cmd="/bin/bash",
            stdin=True,
            tty=True
        )

        self.sock = client.api.exec_start(
            exec_id=exec_instance["Id"],
            detach=False,
            tty=True,
            stream=False,
            socket=True
        )

        self.sock._sock.setblocking(True)
        
        self.output_queue = queue.Queue()
        self.read_thread = threading.Thread(target=self._reader, daemon=True)
        self.read_thread.start()

    def _reader(self):
        try:
            while True:
                data = self.sock._sock.recv(1024)
                if not data:
                    break
                self.output_queue.put(data.decode(errors="ignore"))
        except Exception as e:
            self.output_queue.put(f"[reader error] {e}")

    def read(self):
        if not self.output_queue.empty():
            out = self.output_queue.get()
            # print("[debug]: reading: ", repr(out))
            return out
        return ""

    def write(self, data):
        try:
            self.sock._sock.send(data.encode())
            # print("[DEBUG] writing:", repr(data))
        except Exception as e:
            print(f"[write error] {e}")

    def close(self):
        try:
            self.sock.close()
        except:
            pass

        try:
            self.container.kill()
        except:
            pass

