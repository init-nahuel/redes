import socket
import random
import os
import socketTCP


class socketTCP:
    def __init__(self) -> None:
        self.dest_address = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.orig_address = None
        self.seq = None
        self.parsed_buffer = None
        self.header_buffer = None
        self.content_buffer = None

    @staticmethod
    def parse_segment(msg: str) -> dict[str, str]:
        """Convierte un segmento TCP a un diccionario. Este metodo considera la codificacion
        de headers sin usar directamente bytes, i.e. [SYN]|||[ACK]|||[FIN]|||[SEQ]|||[DATOS]
        """
        values = msg.split('|||')
        keys = ['SYN', 'ACK', 'FIN', 'SEQ', 'DATA']
        parsed_msg = dict(zip(keys, values))

        return parsed_msg

    @staticmethod
    def create_segment(parsed_msg: dict[str, str]) -> str:
        """Convierte el mensaje parseado nuevamente a un segmento TCP.
        """

        return "|||".join(list(parsed_msg.keys()))

    @staticmethod
    def make_tcp_headers(*args) -> str:
        """Crea el header TCP codificado, considera los parametros en orden:
        SYN, ACK, FIN, SEQ.
        """

        to_str_list = [str(arg) for arg in args]

        return "|||".join(to_str_list)

    @staticmethod
    def verify_seq_3way(new_seq: int, actual_seq: int) -> bool:
        """Verifica que el numero de secuencia nuevo se haya incrementado en 1
        durante el 3-way handshake, en tal caso retorna True y False en caso contrario.
        """

        return new_seq - actual_seq == 1

    @staticmethod
    def verify_inc_seq(new_seq: int, actual_seq: int) -> tuple[bool, int]:
        """Verifica que el numero de secuencia nuevo sea mayor que el numero de
        secuencia actual. Retorna una tuple con el valor de verdad y la diferencia.
        """

        diff = new_seq - actual_seq
        return (diff > 0, diff)

    def bind(self, address: tuple[str, int]):
        """Aisgna una direccion de origen (IP, Puerto) al socket socketTCP.
        """

        self.orig_address = address
        self.udp_socket.bind(address)

    def connect(self, address) -> int:
        """Establece el 3-way handshake entre el socket socketTCP cliente y
        el servidor ubicado en la direcction de destino address
        en la que se encuentra escuchando. Retorna uno en caso de establecerse correctamente
        el handshake y 0 en caso contrario.
        """

        self.seq = random.randint(0, 100)
        self.dest_address = address

        status = 0

        # 3-way handshake
        # Envio mensaje SYN Cliente
        self.header_buffer = self.make_tcp_headers(1, 0, 0, self.seq)
        self.udp_socket.sendto(self.header_buffer.encode(), self.dest_address)

        # Recibo SYN+ACK Servidor
        self.header_buffer, _ = self.udp_socket.recvfrom(16)

        self.header_buffer = self.header_buffer.decode()
        self.parsed_buffer = self.parse_segment(self.header_buffer)
        syn, ack, fin, new_seq, _ = [int(val)
                                     for val in self.parsed_buffer.values()]
        if (self.verify_seq_3way(new_seq, self.seq) and syn == 1 and ack == 1 and fin == 0):
            self.seq = new_seq + 1
            self.header_buffer = self.make_tcp_headers(0, 1, 0, self.seq)

            # Envio ACK Cliente
            self.udp_socket.sendto(
                self.header_buffer.enconde(), self.dest_address)

            status = 1
            return status
        else:
            print("----> Posible infiltracion en la conexion, cerrando...")
            os.close()

            return status

    def accept(self) -> tuple[socketTCP, tuple[str, int]]:
        """Establece el 3-way handshake entre el socket socketTCP Servidor y el cliente.
        Retorna una tupla con un nuevo socket socketTCP y la direccion de este nuevo socket."""

        # 3-way handshake
        # Recibo SYN Cliente
        self.header_buffer, client_address = self.udp_socket.recvfrom(16)
        self.header_buffer = self.header_buffer.decode()
        self.parsed_buffer = self.parse_segment(self.header_buffer)
        self.seq = int(self.parsed_buffer['SEQ']) + 1
        syn, ack, fin, _ = [int(val)
                            for val in self.header_buffer.split('|||')]

        if (syn == 1 and ack == 0 and fin == 0):
            self.header_buffer = self.make_tcp_headers(1, 1, 0, self.seq)

            # Envio SYN+ACK
            self.udp_socket.sendto(self.header_buffer, client_address)

        else:
            print("----> Recibido peticion erronea, rechazando...")
            self.seq = None
            self.header_buffer = None
            self.parsed_buffer = None

            return None

        # Recibo ACK Cliente
        self.header_buffer, _ = self.udp_socket.recvfrom(16)
        self.header_buffer = self.header_buffer.decode()
        self.parsed_buffer = self.parse_segment(self.header_buffer)
        syn, ack, fin, new_seq = [int(val)
                                  for val in self.header_buffer.split('|||')]
        if (syn == 1 and ack == 0 and fin == 0 and self.verify_seq_3way(new_seq, self.seq)):
            self.seq = new_seq + 1
            # Envio ACK
            self.udp_socket.sendto(self.make_tcp_headers(
                0, 1, 0, self.seq), client_address)

            # Eliminamos direccion y seq del socket Server y trapasamos estos datos al nuevo socketTCP
            new_address = self.orig_address + random.randint(1, 100)
            bind_address = self.orig_address
            self.orig_address = new_address
            self.seq = 0

            new_socket = socketTCP()
            new_socket.seq = self.seq
            new_socket.bind(bind_address)
            new_socket.dest_address = client_address

            # Devolvemos nueva instancia de socketTCP
            return (new_socket, bind_address)
        else:
            print("----> Handshake erroneo, rechanzando...")
            self.seq = None
            self.header_buffer = None
            self.parsed_buffer = None
            return None
