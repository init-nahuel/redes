import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 5000)

my_socket.bind(address)

buffer, _ = my_socket.recvfrom(22)

size = int(buffer[len(buffer)-4:].decode())

print(f"El largo que tendra el mensaje es {size}")
