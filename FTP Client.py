#Server Client by William Oswald and Neal Todd
#Credit to the helpful resource: https://pymotw.com/3/socket/tcp.html & https://docs.python.org/3/howto/sockets.html



import socket
import sys
import getpass
import CommandList
import getpass


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.168.0.101', 7891)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

#this function is the one of two basic ways to send information, this one sends an variable sized chunk of binary data in packets to the client
def SendBinary(data):

	#This bit sends an integer to the client, informing it how many bits to exspect in the full message
	size = len(data)
	sock.sendall(str(size).encode())
	
	#then it waits for a flag response from the client indicating it has recived the size
	sock.recv(1024)

	#Then it sends the binary data
	sock.sendall(data)

def RecvBinary():

	#First it destingishes the size of the binary data it will be reciving
	size = int(sock.recv(1024).decode())

	#sends an indication flag to the client to indicate it has recived the message
	sock.sendall(b'a')
	
	#prime the pump
	dataRecv = 0
	data = b''

	#Reconstructs the message that the client is sending it, in 1024 byte chunks
	while (dataRecv < size):
		temp = sock.recv(1024)
		data += temp
		dataRecv = len(data)
	
	#once the message is fully assembled, returns the binary data
	return data

#almost exactully the same as the bindary data transfer protocol, however it exspects a string to come through, instead of bindary data
def SendData(data):
	size = len(data)
	sock.sendall(str(size).encode())
	sock.recv(1024)
	sock.sendall(str(data).encode())
	sock.recv(1024)

#almost exactully like RecvBinary, but exspecting a string to come through
def RecvData():
	size = int(sock.recv(1024).decode())
	sock.sendall(b'a')
	
	dataRecv = 0
	data = ""

	while (dataRecv < size):
		temp = sock.recv(1024).decode()
		data += temp
		dataRecv = len(data)

	sock.sendall(b'a')

	return data


#readys a file to be sent to the client
def UploadFile(fileName):

	#opens the file in a read binary mode
	fin = open(fileName, 'rb')
	fileData = fin.read()

	#using the prebuilt functions, sends the file name, then the binary data to the client
	SendData(fileName)
	SendBinary(fileData)

	#closes the file
	fin.close()

	#waits for an indication flag from the client that it has recived the file
	sock.recv(1024)

def DownloadFile():

	#virst the file name is declared
	fileName = RecvData()

	#then the files binary data is sent through
	fileData = RecvBinary()
	
	#then the file is reconstructed
	fin = open(fileName, 'wb')
	fin.write(fileData)
	#Then we save the file
	fin.close()

	sock.sendall(b'a')


try:

	print("FTP Login Screen")
	userName = input("User Name: ")
	password = getpass.getpass("Password: ")

	#sends the username and password to the server for validation
	SendData(userName)
	RecvData()
	SendData(password)

	temp = RecvData()
	LoginAccepted = False


	#checks to see if login was sucsessful
	if (temp == 'true'):
		LoginAccepted = True

	#if bad connection
	print('\n\n', RecvData())
	if (LoginAccepted == False):
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	else:
		print (CommandList.LIST)

	
	#main loop of the function, which impliments all the functions from the assignment specs
	while LoginAccepted:
		Cint = str(input("\nEnter command: "))

		if(Cint == "login"):
			print(CommandList.LIST)
		elif(Cint == "ls"):
			SendData(str("ls"))
			print(RecvData())
		elif(Cint == "cd"):
			SendData(str("cd"))
			SendData(input('Input new Directory: '))
			print(RecvData())
		elif(Cint == "put"):
			SendData(str("put"))
			UploadFile(input('What file do you want to upload? (Include exstention)\n'))
		elif(Cint == "get"):
			SendData(str("get"))
			fileName = input('What file do you want to download? ')
			SendData(fileName)
			DownloadFile()
			print("Download Finished")
		elif(Cint == "mput"):
			temp = input("What files do you want to upload? (Space dilimited)")
			temp = str(temp).split(' ')
			for i in temp:
				SendData(str("put"))
				UploadFile(i)
			
		elif(Cint == "mget"):
			temp = input("What files do you want to download?(Space dilimited)")
			temp = str(temp).split(' ')
			for i in temp:
				SendData(str("get"))
				SendData(i)
				DownloadFile()


			print("Download Complete")

		#close the connection
		elif(Cint == 90):
			SendData(str(90))
			sock.shutdown(socket.SHUT_RDWR)
			sock.close()
			break
		else:
			print('invalid input')

			

finally:
	print('closing socket')
		#sock.close()
