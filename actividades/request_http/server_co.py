import socket
from utils import *

# definimos el tamaño del buffer de recepción y la secuencia de fin de mensaje
buff_size = 4
end_of_message = "\n"
new_socket_address = ('localhost', 5000)

print('Creando socket - Servidor')
# armamos el socket
# los parámetros que recibe el socket indican el tipo de conexión
# socket.SOCK_STREAM = socket orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# le indicamos al server socket que debe atender peticiones en la dirección address
# para ello usamos bind
server_socket.bind(new_socket_address)

# luego con listen (función de sockets de python) le decimos que puede
# tener hasta 3 peticiones de conexión encoladas
# si recibiera una 4ta petición de conexión la va a rechazar
server_socket.listen(3)

# nos quedamos esperando a que llegue una petición de conexión
print('... Esperando clientes')
while True:
    # cuando llega una petición de conexión la aceptamos
    # y se crea un nuevo socket que se comunicará con el cliente
    new_socket, new_socket_address = server_socket.accept()

    # luego recibimos el mensaje usando la función que programamos
    # esta función entrega el mensaje en string (no en bytes) y sin el end_of_message
    recv_message = receive_full_mesage(new_socket, buff_size, end_of_message)

    print(f' -> Se ha recibido el siguiente mensaje: {recv_message}')

    # respondemos indicando que recibimos el mensaje
    response_message = f"Se ha sido recibido con éxito el mensaje: {recv_message}"

    # el mensaje debe pasarse a bytes antes de ser enviado, para ello usamos encode
    new_socket.send(response_message.encode())

    # cerramos la conexión
    # notar que la dirección que se imprime indica un número de puerto distinto al 5000
    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")

    # seguimos esperando por si llegan otras conexiones