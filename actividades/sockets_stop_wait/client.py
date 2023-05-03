import socket
import sys
from utils import *

# python3 cliente.py localhost 8000 < archivo.txt
program_name, ip, port = sys.argv
file = input()

# OJO CON EL EOF CUANDO EL ARCHIVO ESTA VACIO, LANZA LA EXEPCION EOFError

address = (ip, int(port))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(file)
# Enviamos los trozos de 16 bytes
# msg_bytes = file.encode()
# send_message(msg_bytes, client_socket, address, size=len(msg_bytes))

# client_socket.close()