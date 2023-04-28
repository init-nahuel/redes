import socket
import sys
import json
from utils import *

filename = sys.argv[1]
path = sys.argv[2]

# Extraemos las uris que se encuentran prohibidas
json_file = open(path+'/'+filename, "r")
data = json.load(json_file)
blocked_uris = data['blocked']

# Parte tarea en que se enviaba como response un archivo html al cliente
# f = open("index.html", "r")
# response = f.read()

# definimos el tamaño del buffer de recepción y address
buff_size = 50
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
    message_from_client = receive_full_mesage_http(new_socket, buff_size)

    print(f' -> Se ha recibido el siguiente mensaje: \n{message_from_client}')

    # Parseamos el mensaje para obtener el host y uri
    host = get_host(from_http_to_data(message_from_client)['start_line'])
    uri = get_uri(message_from_client)
    
    # Revisamos si es posible acceder al recurso
    if (is_available(uri, blocked_uris)):
        # Creamos el socket con el cual nuestro proxy se conectara al servidor de destino
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"  ->Conectandose al host: {host}")

        # Nos conectamos al servidor de destino y enviamos la request
        proxy_socket.connect((host, 80)) # Puerto 80 es el puerto por defecto para HTTP

        if (host == 'cc4303.bachmann.cl'): # En este caso agregamos el header requerido
            message_from_client = add_header(message_from_client, 'X-ElQuePregunta', 'Nahuel')

        proxy_socket.send(message_from_client.encode())

        print(f' -> Enviando request al servidor: \n{message_from_client}')

        # Recibimos la response desde el servidor
        response_from_server = receive_full_mesage_http(proxy_socket, buff_size)

        print(f' -> Respuesta recibida del servidor: \n{response_from_server}')

        # Reemplazamos las palabras prohibidas en caso de existir
        response_from_server = replace_forbidden_words(response_from_server, data['forbidden_words'])

        print(f' -> Respuesta del servidor filtrada: \n{response_from_server}')
        
        # Respondemos al cliente con la response del servidor
        new_socket.send(response_from_server.encode())

        # Cerramos la conexion
        proxy_socket.close()
    else:
        # En caso de que el recurso sea prohibido se envia un mensaje con el codigo y descripcion del error
        response_error_dict = {'start_line': "HTTP/1.1 403 Forbidden"}
        response = from_data_to_http(response_error_dict)
        
        print(f' -> Peticion Denegada, enviando respuesta al cliente: \n{response}')
        
        new_socket.send(response.encode())

    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")
