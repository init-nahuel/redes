import socket

def send_message(file: bytes, socket: socket.socket, address: tuple[str, str], size: int) -> None:
    """Envia el archivo file mediante el socket hacia la direccion address, si el
    mensaje es de largo mayor a 16 bytes lo divide en paquetes de este largo
    maximo y los envia secuencialmente.
    """
    
    while (size > 16):
        socket.sendto(file[:16], address) # Enviamos los primeros 16 bytes
        file = file[16:]
        size = len(file)
    
    socket.sendto(file, address)