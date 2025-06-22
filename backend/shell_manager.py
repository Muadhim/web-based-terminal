import os
import pty
import select

class ShellSession:
    def __init__(self, shell_path="/bin/bash"):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvp(shell_path, [shell_path])

    def read(self):
        if select.select([self.fd], [], [], 0)[0]:
            return os.read(self.fd, 1024).decode(errors="ignore")
        return ""

    def write(self, data):
        os.write(self.fd, data.encode())

    def close(self):
        os.close(self.fd)
