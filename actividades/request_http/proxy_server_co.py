import socket
import sys
import json
from utils import *

filename = sys.argv[1]
path = sys.argv[2]

json_file = open(path+'/'+filename, "r")
data = json.load(json_file)
name = data["name"]

f = open("index.html", "r")
html_file = f.read()
response = create_http_response(html_file, name=name)

# definimos el tamaño del buffer de recepción
buff_size = 4
new_socket_address = ('localhost', 8000)

print('Creando socket - Servidor')
# Creamos el socket orientado a conexion
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# le indicamos al server socket que debe atender peticiones en la dirección address
# para ello usamos bind
server_socket.bind(new_socket_address)

# Como es un servidor encargado de escuchar peticiones simplemente escuchamos
# sin un limite (se aplica el valor por default del metodo).
server_socket.listen()

# nos quedamos esperando a que llegue una petición de conexión
print('... Esperando clientes')
while True:
    # cuando llega una petición de conexión la aceptamos
    # y se crea un nuevo socket que se comunicará con el cliente
    new_socket, new_socket_address = server_socket.accept()

    # luego recibimos el mensaje HTTP decodificado
    recv_message = receive_full_mesage_http(new_socket, buff_size)

    print(f' -> Se ha recibido el siguiente mensaje: \n{recv_message}')

    # Creamos el socket con el cual nuestro proxy se conectara al servidor de destino
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Nos conectamos a al servidor de destino y enviamos la request
    proxy_socket.connect(('example.com', 8000)) # TODO: ver por que no conecta :(
    proxy_socket.send(recv_message.encode()) 

    print(f' -> Enviando request al servidor: \n{recv_message}')

    # Recibimos la response desde el servidor
    response_from_server = receive_full_mesage_http(proxy_socket, buff_size)

    print(f' -> Respuesta recibida del servidor: \n{response_from_server}')
    
    # Respondemos al cliente con la response del servidor
    new_socket.send(response_from_server.encode())

    # Respondemos con el mismo mensaje HTTP, codificandolo
    # new_socket.send(response.encode())

    # Cerramos las conexiones
    proxy_socket.close()
    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")
