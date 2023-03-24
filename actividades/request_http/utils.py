# import os
import re

# Retorna -1 si el header Content-Length no se encuentra por completo en message, 
# de otra forma retorna el valor de este header.
# OBS: la expresion regular como tal no necesitaria hacer math de espacios luego del numero
# pues por formato debiese de ir de inmediato '\r\n'
def contains_length_header(message):
    msg = message.lower()
    regex = re.compile(r'Content-Length: (\d*)\r\n')
    content_lenght = regex.search(message)
    try:
        return content_lenght.group(1)
    except:
        return -1

# esta función se encarga de recibir el mensaje completo desde el cliente
# en caso de que el mensaje sea más grande que el tamaño del buffer 'buff_size', esta función va esperar a que
# llegue el resto

def receive_full_mesage_http(connection_socket, buff_size):

    # recibimos la primera parte del mensaje
    end_sequence = '\r\n'
    recv_message = connection_socket.recv(buff_size)
    full_message = recv_message

    # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
    is_end_of_message = contains_end_of_message(full_message.decode(), end_sequence)

    # Obtenemos el HEAD
    while not is_end_of_message:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)

        # lo añadimos al mensaje "completo"
        full_message += recv_message

        # verificamos si es la última parte del mensaje
        is_end_of_message = contains_end_of_message(full_message.decode(), end_sequence)

    # removemos la secuencia de fin de mensaje, esto entrega un mensaje en string
    full_message = remove_end_of_message(full_message.decode(), end_sequence)

    # finalmente retornamos el mensaje
    return full_message


def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)


def remove_end_of_message(full_message, end_sequence):
    index = full_message.rfind(end_sequence)
    return full_message[:index]

def from_http_to_data(message):
    # Las lineas comentadas sirven en caso de que el mensaje HTTP se encuentre con saltos de linea y no un solo un string con los
    # respectivos \r\n y \r\n\r\n
    head, body = message.split('\r\n\r\n')
    # head, body = message.split(2*os.linesep)

    headers = head.split('\r\n')
    # headers= head.split('\n')

    start_line = headers[0]
    http_dict = {'start_line': start_line}

    for header in headers[1:]:
        param, detail = header.split(':')
        http_dict[param] = detail

    http_dict['body'] = body

    return http_dict

def from_data_to_http(http_dict):
    http_message = http_dict['start_line'] + '\r\n'
    del http_dict['start_line']

    for key, value in http_dict.copy().items():
        if (len(http_dict) == 1):
            http_message += '\r\n\r\n' + value
        else:
            http_message += key + value + '\r\n'
        del http_dict[key]

    return http_message
    


response = """POST /cgi-bin/process.cgi HTTP/1.1\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)\r\nHost: www.tutorialspoint.com\r\nContent-Type: text/xml; charset=utf-8\r\nContent-Length: length\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate\r\nConnection: Keep-Alive\r\n\r\n<?xml version="1.0" encoding="utf-8"?><string xmlns="http://clearforest.com/">string</string>"""

# response = """POST /cgi-bin/process.cgi HTTP/1.1
# User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
# Host: www.tutorialspoint.com
# Content-Type: text/xml; charset=utf-8
# Content-Length: length
# Accept-Language: en-us
# Accept-Encoding: gzip, deflate
# Connection: Keep-Alive

# <?xml version="1.0" encoding="utf-8"?>
# <string xmlns="http://clearforest.com/">string</string>"""

http_dict = from_http_to_data(response)
http_message = from_data_to_http(http_dict)