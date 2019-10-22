
#Server Application by William Oswald and Neal Todd
#Credit to the helpful resource: https://pymotw.com/3/socket/tcp.html & https://docs.python.org/3/howto/sockets.html


import socket
import sys
import os

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('', 7891)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

#This directory is used as a reference for all files that the client requests to download, and is used for the location for files to be uploaded to. 
currentDirectory = "Server Files"


#this function is called when the client would like an update on the files under the current directory
def DirectoryUpdate():
	#get a list of all files under current directory
	Files = os.listdir(currentDirectory)

	#Creates a header for the string to be returned to the client
	temp = "Files Under " + currentDirectory + '\n'

	#goes through each item adding it to the temp string, creating a neatly formed list
	for i in Files:
		temp = temp + i + '\n'
		
	return temp

#this function checks the password entered to ensure that it's a univeristy account
def LoginValidate(userName, Password):

	jag = '@jagmail.southalabama.edu'
	
	if (Password[Password.find('@'):] == jag):
		return True

	return False

#this function is the one of two basic ways to send information, this one sends an variable sized chunk of binary data in packets to the client
def SendBinary(data):
	
	#This bit sends an integer to the client, informing it how many bits to exspect in the full message
	size = len(data)
	connection.sendall(str(size).encode())

	#then it waits for a flag response from the client indicating it has recived the size
	connection.recv(1024)

	#Then it sends the binary data
	connection.sendall(data)

def RecvBinary():

	#First it destingishes the size of the binary data it will be reciving
	size = int(connection.recv(1024).decode())

	#sends an indication flag to the client to indicate it has recived the message
	connection.sendall(b'a')
	
	#prime the pump
	dataRecv = 0
	data = b''

	#Reconstructs the message that the client is sending it, in 1024 byte chunks
	while (dataRecv < size):
		temp = connection.recv(1024)
		data += temp
		dataRecv = len(data)

	#once the message is fully assembled, returns the binary data
	return data

#almost exactully the same as the bindary data transfer protocol, however it exspects a string to come through, instead of bindary data
def SendData(data):
	size = len(data)
	connection.sendall(str(size).encode())
	connection.recv(1024)
	connection.sendall(str(data).encode())
	connection.recv(1024)

#almost exactully like RecvBinary, but exspecting a string to come through
def RecvData():
	size = int(connection.recv(1024).decode())
	connection.sendall(b'a')
	
	dataRecv = 0
	data = ""

	while (dataRecv < size):
		temp = connection.recv(1024).decode()
		data += temp
		dataRecv = len(data)

	connection.sendall(b'a')
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
	connection.recv(1024)

#readys the server to recive a file
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

	connection.sendall(b'a')





# Listen for incoming connections
sock.listen(1)
while True:

	

    # Wait for a connection
	print('waiting for a connection')
	connection, client_address = sock.accept()
	try:
		print('connection from', client_address)
		print('Waiting for username and password from user...')
		userName = RecvData()
		SendData(b'a')	#a flag to indicate the message made it through to the client
		password = RecvData()

		#checks the login details
		LoginAccepted = LoginValidate(userName, password)
		
		print('User loggin was: \nUsername: ', userName, '\nPassword: ', password , 'Valid Login: ', LoginAccepted)


		if (LoginAccepted):
			SendData('true')
			print('User Loggin was sucsessful, waiting for further responce')
			SendData('User Loggin was sucsessful, waiting for further responce')
		else:
			SendData('false')
			print('User Loggin was sucsessful, waiting for further responce')
			SendData('User Loggin was sucsessful, waiting for further responce')
			break

		
		#this is the main block of the program, calling the above functions to impliment the specs of the assignment
		while LoginAccepted:

			Cint = str(RecvData())
			if(Cint == "ls"):
				print("Sending Directory")
				SendData(DirectoryUpdate())
			elif(Cint == "cd"):
				print("Updating Direcotry, waitng for user input")
				currentDirectory = RecvData()
				print("Directory updated to: ", currentDirectory)
				SendData(DirectoryUpdate())
			elif(Cint == "put"):
				print("downloading file")
				DownloadFile()
				print("Download complete")
			elif(Cint == "get"):
				fileName = RecvData()
				print("uploading file: ", fileName)
				UploadFile(fileName)
				print("Upload Complete")
			elif(Cint == "mput"):
				#mput does not truely exist on the server side, we just have the client call the put command multiple times
				pass
			elif(Cint == "mget"):
				#mget is much the same with the mput command, and does not exist on the server side
				pass
			elif(Cint == 90):
				LoginAccepted = False
				break


	finally:
		# Clean up the connection
		print("Closing connection")
		#connection.close()
