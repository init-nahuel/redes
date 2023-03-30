import re

def is_available(uri, blocked_uris):
    for u in blocked_uris:
        if (u == uri):
            return False
    return True

def get_uri(msg):
    return msg.split(' ')[1]

def get_host(message):
    regex = re.compile(r"http://((\w+|\.)*(.com|.cl))")
    uri = regex.search(message)
    try:
        return str(uri.group(1))
    except AttributeError:
        return 'a'

def content_length_header(message):
    """Retorna -1 si el header Content-Length no se encuentra por completo en message,
    de otra forma retorna el largo declarado.
    La expresion regular se rige por el formato estandar que debiesen tener los mensajes HTTP.
    """

    regex = re.compile(r'Content-Length: (\d+)\r\n')
    content_lenght = regex.search(message)
    try:
        return int(content_lenght.group(1))
    except AttributeError:
        return -1

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

    # Recibimos el BODY (En caso de existir)
    full_message = full_message.decode()
    content_length = content_length_header(full_message)
    if content_length > 0:
        full_message += connection_socket.recv(content_length).decode()

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

    head, body = message.split('\r\n\r\n')

    headers = head.split('\r\n')

    start_line = headers[0]
    http_dict = {'start_line': start_line}

    for header in headers[1:]:
        param, detail = header.split(':', 1)
        http_dict[param] = detail

    if (body != ''):
        http_dict['body'] = body

    return http_dict

def from_data_to_http(http_dict):
    """Retorna un mensaje HTTP creado a partir de los componentes del diccionario.
    """

    if (len(http_dict) == 1):
        http_message = http_dict['start_line'] + '\r\n\r\n'
    else:
        http_message = http_dict['start_line'] + '\r\n'
    del http_dict['start_line']
    copy_http_dict = http_dict.copy()

    for key, value in copy_http_dict.items():
        if (len(http_dict) == 1 and 'Content-Length' in copy_http_dict):
            http_message += '\r\n' + value
        elif (len(http_dict) == 1):
            http_message += key + ':' + value + '\r\n\r\n'
        else:
            http_message += key + ':' + value + '\r\n'
        del http_dict[key]

    return http_message

def add_header(http_message, header_name, header_content):
    """Agrega un nuevo header a un mensaje HTTP, este nuevo header
    se encontrara justo debajo de la start-line del mensaje HTTP,
    por tanto sera el primer header.
    """
    
    http_dict = from_http_to_data(http_message)
    start_line = http_dict['start_line']
    del http_dict['start_line']
    http_dict = {'start_line': start_line, header_name:' '+str(header_content)} | http_dict
    new_http_msg = from_data_to_http(http_dict)
    
    return new_http_msg

def replace_forbidden_words(http_msg, forb_words):
    """Reemplaza las palabras prohibidas en un mensaje HTTP dado una lista
    que contiene diccionarios con las palabras prohibidas y su reemplazo.
    """
    new_http_dict =  from_http_to_data(http_msg)
    body = new_http_dict['body']
    
    for d in forb_words:
        for key, value in d.items():
            if key in body:
                body = body.replace(key, value)
    
    new_http_dict['body'] = body
    new_size = len(body.encode())
    new_http_dict['Content-Length'] = ' '+str(new_size)
    new_msg = from_data_to_http(new_http_dict)
    
    return new_msg