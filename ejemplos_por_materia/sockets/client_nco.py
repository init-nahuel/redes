import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

send_address = ("localhost", 5000)

message = "Hola que tal"

client_socket.sendto(message.encode(), send_address)

message_recv, sex = client_socket.recvfrom(1024)

print(f"Received message: {message_recv.decode()}")

client_socket.close()