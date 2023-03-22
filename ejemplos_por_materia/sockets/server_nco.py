import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ("localhost", 5000)

server_socket.bind(address)

message, sended_address = server_socket.recvfrom(1024)

print(f"Message: {message.decode()}")

server_socket.sendto(message, sended_address)

server_socket.close()