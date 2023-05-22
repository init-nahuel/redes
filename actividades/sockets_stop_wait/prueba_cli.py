import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 5000)

my_socket.sendto('0|||1|||1|||121|||'.encode() + '1234'.encode(), address)
