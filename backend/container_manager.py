import docker
import os

import docker.errors

client = docker.from_env()


class ContainerManager:
    def __init__(self, base_dir="user_data"):
        self.base_dir = os.path.abspath(base_dir)
        self.containers = {}

        os.makedirs(self.base_dir, exist_ok=True)

    def get_or_create_container(self, username):
        container_name = f"user_{username[:16]}"

        try:
            container = client.containers.get(container_name)

            if container.status != "running":
                container.start()

            self.containers[username] = container
            return container

        except docker.errors.NotFound:
            # container doesn't exist yet - create it
            user_home = self._create_user_home(username)

            container = client.containers.run(
                "ubuntu:20.04",
                command="/bin/bash",
                stdin_open=True,
                detach=True,
                tty=True,
                remove=False,
                network_mode="none",
                cap_drop=["ALL"],
                cap_add=["CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "FOWNER", "KILL"],
                read_only=True,
                tmpfs={"/tmp": ""},
                volumes={user_home: {"bind": f"/home/{username}", "mode": "rw"}},
                mem_limit="128m",
                cpu_period=100000,
                cpu_quota=50000,
                name=f"user_{username[:16]}",
            )

            self.containers = container
            return container

    def stop_container(self, username):
        container = self.containers.get(username)

        if container:
            try:
                container.kill()
            except:
                pass

            try:
                container.remove(force=True)
            except:
                pass

            del self.container[username]

    def _create_user_home(self, username):
        path = os.path.join(self.base_dir, username)
        os.makedirs(path, exist_ok=True)
        os.chmod(path, 0o700)
        return path
