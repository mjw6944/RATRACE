#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

#ifdef _MSC_VER
#pragma comment(lib, "Ws2_32.lib")
#endif

#define MAX_COMMAND_LENGTH	256
#define RECONNECT_DELAY		5000 // milliseconds

void helpCommand(SOCKET clientSocket) {
	char helpText[] = "Available commands:\n"
					  "help - Display this help message\n"
					  "command1 - Description of command 1\n"
					  "command2 - Description of command 2\n"
					  "command3 - Description of command 3\n";
	send(clientSocket, helpText, strlen(helpText), 0);
}

void handleCommand(char* command, SOCKET clientSocket) {
	if(strcmp(command, "help") == 0) {
		helpCommand(clientSocket);
	}
	else if(strcmp(command, "command1") == 0) {
		// Implement command 1 logic here
	}
	else if(strcmp(command, "command2") == 0) {
		// Implement command 2 logic here
	}
	else if(strcmp(command, "command3") == 0) {
		// Implement command 3 logic here
	}
	else {
		char unknownCommand[] = "Unknown command. Type 'help' for available commands.\n";
		send(clientSocket, unknownCommand, strlen(unknownCommand), 0);
	}
}

SOCKET connectToServer() {
	WSADATA wsaData;
	SOCKET ConnectSocket = INVALID_SOCKET;
	struct addrinfo *result = NULL, *ptr = NULL, hints;

	WSAStartup(MAKEWORD(2,2), &wsaData);

	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	getaddrinfo("192.168.197.222", "5555", &hints, &result);

	for(ptr=result; ptr != NULL ;ptr=ptr->ai_next) {
		ConnectSocket = socket(ptr->ai_family, ptr->ai_socktype, ptr->ai_protocol);
		connect(ConnectSocket, ptr->ai_addr, (int)ptr->ai_addrlen);
	}

	freeaddrinfo(result);
	return ConnectSocket;
}

int main() {
	SOCKET ConnectSocket;
	char recvbuf[MAX_COMMAND_LENGTH];
	int iResult;
	int recvbuflen = MAX_COMMAND_LENGTH;

	while(1) {
		ConnectSocket = connectToServer();

		if(ConnectSocket == INVALID_SOCKET) {
			printf("Failed to connect, retrying in %d seconds...\n", RECONNECT_DELAY/1000);
			Sleep(RECONNECT_DELAY);
			continue;
		}

		printf("Connected to server\n");

		while(1) {
			iResult = recv(ConnectSocket, recvbuf, recvbuflen, 0);

			if(iResult > 0) {
				recvbuf[iResult] = '\0';
				handleCommand(recvbuf, ConnectSocket);
			}
			else {
				printf("Connection closed or error occurred, reconnecting...\n");
				closesocket(ConnectSocket);
				Sleep(RECONNECT_DELAY);
				break;
			}
		}
	}

	WSACleanup();
	return 0;
}
