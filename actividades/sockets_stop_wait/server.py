# import socket
from socketTCP import SocketTCP

address = ('localhost', 8000)

server_socketTCP = SocketTCP()
server_socketTCP.bind(address)

print("----> Realizando Handshake")

connection_socketTCP, new_address = server_socketTCP.accept()

print("----> Handshake finalizado")
