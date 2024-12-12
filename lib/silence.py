import os

stderr_fd = None

def on():
    global stderr_fd
    if stderr_fd is None:
        stderr_fd = os.dup(2)
    os.close(2)

def off():
    global stderr_fd
    if stderr_fd is not None:
        os.dup2(stderr_fd, 2)
