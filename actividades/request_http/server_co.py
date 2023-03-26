import socket
from utils import *

# definimos el tamaño del buffer de recepción y la secuencia de fin de mensaje
buff_size = 4
end_of_message = "\r\n\r\n"
new_socket_address = ('localhost', 8000)

print('Creando socket - Servidor')
# armamos el socket
# los parámetros que recibe el socket indican el tipo de conexión
# socket.SOCK_STREAM = socket orientado a conexión
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
    recv_message = receive_full_mesage_http(new_socket, buff_size, end_of_message)

    print(f' -> Se ha recibido el siguiente mensaje: {recv_message}')

    # respondemos indicando que recibimos el mensaje
    response_message = f"Se ha sido recibido con éxito el mensaje: {recv_message}"
    # http_dict = from_http_to_data(recv_message)
    # response_message = recv_message
    # response = from_data_to_http(http_dict)

    # Respondemos con el mismo mensaje HTTP, codificandolo
    new_socket.send(recv_message.encode())

    # cerramos la conexión
    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")

    # seguimos esperando por si llegan otras conexiones