import os
import re

response = """POST /cgi-bin/process.cgi HTTP/1.1
User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
Host: www.tutorialspoint.com
Content-Type: text/xml; charset=utf-8
Content-Length: 123
Accept-Language: en-us
Accept-Encoding: gzip, deflate
Connection: Keep-Alive

# <?xml version="1.0" encoding="utf-8"?>
# <string xmlns="http://clearforest.com/">string</string>"""

# response = """POST /cgi-bin/process.cgi HTTP/1.1\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)\r\nHost: www.tutorialspoint.com\r\nContent-Type: text/xml; charset=utf-8\r\nContent-Length: 123\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate\r\nConnection: Keep-Alive\r\n\r\n<?xml version="1.0" encoding="utf-8"?><string xmlns="http://clearforest.com/">string</string>"""

def content_length_header(message):
    """Retorna -1 si el header Content-Length no se encuentra por completo en message,
    de otra forma retorna el largo declarado.
    La expresion regular se rige por el formato estandar que debiesen tener los mensajes HTTP.
    """

    # regex = re.compile(r'Content-Length: (\d+)\r\n')
    regex = re.compile(r'Content-Length: (\d+)'+os.linesep)
    content_lenght = regex.search(message)
    try:
        return int(content_lenght.group(1))
    except AttributeError:
        return -1
    
assert content_length_header(response) == 123

def receive_full_mesage_http(connection_socket, buff_size, end_sequence='\r\n\r\n'):
    """Recibe el mensaje HTTP completo desde el cliente, primero recibe el HEAD
    y luego recibe el BODY a traves de la obtencion
    del largo de este, por ultimo retorna el mensaje HTTP decodificado.
    Por ahora se considera que el contenido de los mensajes es texto plano y no
    imagenes, por eso se retorna
    decodificado el mensaje.
    """

    recv_message = connection_socket.recv(buff_size)
    full_message = recv_message

    is_end_of_message = contains_end_of_head(full_message.decode(), end_sequence)

    # Recibimos el HEAD (\r\n\r\n)
    while not is_end_of_message:
        recv_message = connection_socket.recv(buff_size)

        full_message += recv_message

        is_end_of_message = contains_end_of_head(full_message.decode(), end_sequence)

    # Recibimos el BODY
    full_message = full_message.decode()
    index_begin_body = full_message.index(end_sequence) + len(end_sequence) - 1
    content_length = content_length_header(full_message)
    body_buff_size = content_length - len(full_message[index_begin_body:])
    print(f"body_buff_size: {body_buff_size}")
    print(f"content_length: {content_length}")
    full_message += connection_socket.recv(body_buff_size).decode()

    return full_message

def contains_end_of_head(message, end_sequence):
    return end_sequence in message

def from_http_to_data(message):
    """Retorna un diccionario con los componentes del mensaje HTTP.
    Las llaves se encuentran clasificadas en start_line, headers y body.
    Por ahora considera los separadores del formato estandar de envio de mensajes HTTP.
    Es necesario mencionar que dada la forma en que se hace el split de los string para separar
    los headers de la descripcion de este, a la hora de volver a generar el mensaje HTTP
    con from_data_to_http(), el mensaje generado volvera a mantener los estandares
    de formato.
    """
    # Las lineas comentadas sirven en caso de que el mensaje HTTP se encuentre con saltos de linea y no un solo un string con los
    # respectivos \r\n y \r\n\r\n
    # head, body = message.split('\r\n\r\n')
    head, body = message.split(2*os.linesep)

    # headers = head.split('\r\n')
    headers= head.split(os.linesep)

    start_line = headers[0]
    http_dict = {'start_line': start_line}

    for header in headers[1:]:
        param, detail = header.split(':')
        http_dict[param] = detail

    http_dict['body'] = body

    return http_dict

def from_data_to_http(http_dict):
    """Retorna el mensaje HTTP original"""

    http_message = http_dict['start_line'] + '\r\n'
    del http_dict['start_line']

    for key, value in http_dict.copy().items():
        if (len(http_dict) == 1):
            http_message += '\r\n\r\n' + value
        else:
            http_message += key + value + '\r\n'
        del http_dict[key]

    return http_message
