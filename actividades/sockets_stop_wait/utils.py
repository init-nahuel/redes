from socketTCP import socketTCP
import socket


def send_message(file: bytes, socket: socket.socket, address: tuple[str, int], header_tcp,  size: int) -> None:
    """Envia el archivo file mediante el socket UDP hacia la direccion address, si el
    mensaje es de largo mayor a 16 bytes lo divide en paquetes de este largo
    maximo y los envia secuencialmente.
    """

    # Caso el largo del mensaje es mayor a 16 bytes
    while (size > 16):
        socket.sendto(header_tcp.encode() + file[:16], address)
        file = file[16:]
        size = len(file)

    # Enviamos el mensaje completo si es menor a 16 bytes o lo
    # restante en caso de haber pasado por el while
    socket.sendto(header_tcp.encode() + file, address)


def receive_message(rcv_socket: socket.socket):

    # Primero recibimos el header (largo fijo codificado: 16)
    msg, address = rcv_socket.recvfrom(16)

    # TODO: Mas adelante hay que manejar el SEQ del header para saber el largo del contenido

    if (int(socketTCP.parse_segment(msg.decode())['SYN']) == 1 or int(socketTCP.parse_segment(msg.decode())['ACK']) == 1):
        return (msg.decode(), "", address)

    content_msg, _ = rcv_socket.recvfrom(16)

    # Retorna el header decodificado y el contenido del mensaje codificado
    # luego deben unirse todas las partes para decodificarlo
    return (msg.decode(), content_msg, address)
