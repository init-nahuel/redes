import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('localhost', 8000)
server_socket.bind(address)

while True:
    msg,_ = server_socket.recvfrom(16)
    print(msg.decode())