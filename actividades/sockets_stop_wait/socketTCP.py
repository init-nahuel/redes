from __future__ import annotations
import socket
import random

# Indica el largo maximo del tamanho del mensaje que se enviara/recibira, este largo
# incluye el largo del header adicionalmente
DATA_LEN = 50


class SocketTCP:
    def __init__(self) -> None:
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_address = None
        self.orig_address = None
        self.seq = None
        self.parsed_buffer = None
        self.header_buffer = None
        self.content_buffer = None

        # Timeout (5 segundos)
        self.timeout = 5

        # Registro cantidad de datos enviados/leidos
        self.sended_data_len = 0
        self.readed_data_len = 0

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
        """Verifica que el numero de secuencia nuevo new_seq se haya incrementado en 2
        durante los pasos del 3-way handshake, con respecto al numero de secuencia actual_seq, que posee
        el emisor, en tal caso retorna True y False en caso contrario.
        """

        return new_seq - actual_seq == 2

    @staticmethod
    def verify_inc_seq(new_seq: int, actual_seq: int) -> tuple[bool, int]:
        """Verifica que el numero de secuencia nuevo sea mayor que el numero de
        secuencia actual. Retorna una tuple con el valor de verdad y la diferencia.
        """

        diff = new_seq - actual_seq
        return (diff > 0, diff)

    def bind(self, address: tuple[str, int]):
        """Aisgna una direccion de origen (IP, Puerto) al socket SocketTCP.
        """

        self.orig_address = address
        self.udp_socket.bind(address)

    def connect(self, address) -> int:
        """Establece el 3-way handshake entre el socket SocketTCP cliente y
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

        print(f"----> Enviando mensaje SYN a Servidor: {self.header_buffer}")
        self.udp_socket.sendto(self.header_buffer.encode(), self.dest_address)

        # Recibo SYN+ACK Servidor
        self.header_buffer, new_socket_address = self.udp_socket.recvfrom(16)
        self.header_buffer = self.header_buffer.decode()
        print(
            f"----> Recibido mensaje SYN+ACK desde Servidor: {self.header_buffer}")

        self.dest_address = new_socket_address
        self.parsed_buffer = self.parse_segment(self.header_buffer)
        syn, ack, fin, new_seq = [int(val)
                                  for val in self.parsed_buffer.values()]

        # En verify_seq_3way sumamos 1 pues en el primer SYN del Cliente va el SEQ sin incremento
        if (self.verify_seq_3way(new_seq + 1, self.seq) and syn == 1 and ack == 1 and fin == 0):
            self.seq = new_seq

            # Envio ACK Cliente
            self.header_buffer = self.make_tcp_headers(0, 1, 0, self.seq + 1)

            print(
                f"----> Enviando mensaje ACK de confirmacion a Servidor: {self.header_buffer}")
            self.udp_socket.sendto(
                self.header_buffer.encode(), self.dest_address)
        else:
            print("----> Posible infiltracion en la conexion, cerrando...")

            return status

        # Recibo ACK Servidor (Stop & Wait)
        self.header_buffer, _ = self.udp_socket.recvfrom(16)
        self.header_buffer = self.header_buffer.decode()
        print(
            f"----> Recibido mensaje ACK por Servidor, paso Stop & Wait: {self.header_buffer}")

        self.parsed_buffer = self.parse_segment(self.header_buffer)
        syn, ack, fin, new_seq = [int(val)
                                  for val in self.parsed_buffer.values()]

        if (self.verify_seq_3way(new_seq, self.seq) and syn == 0 and ack == 1 and fin == 0):
            self.seq = new_seq

            status = 1
            return status
        else:

            return status

    def accept(self) -> tuple[SocketTCP, tuple[str, int]] | None:
        """Establece el 3-way handshake entre el socket SocketTCP Servidor y el cliente.
        Retorna una tupla con un nuevo socket SocketTCP y la direccion de este nuevo socket."""

        # Creamos el nuevo socket para el
        new_socket = SocketTCP()

        # 3-way handshake
        # Recibo SYN Cliente
        new_socket.header_buffer, client_address = self.udp_socket.recvfrom(16)
        new_socket.dest_address = client_address

        # Bind del nuevo socket
        # new_socket.bind(client_address)

        new_socket.header_buffer = new_socket.header_buffer.decode()
        print(
            f"----> Recibido mensaje SYN por Cliente: {new_socket.header_buffer}")

        new_socket.parsed_buffer = new_socket.parse_segment(
            new_socket.header_buffer)
        new_socket.seq = int(new_socket.parsed_buffer['SEQ'])
        syn, ack, fin, _ = [int(val)
                            for val in new_socket.header_buffer.split('|||')]

        if (syn == 1 and ack == 0 and fin == 0):
            new_socket.header_buffer = new_socket.make_tcp_headers(
                1, 1, 0, new_socket.seq + 1)

            # Envio SYN+ACK
            print(
                f"----> Enviando mensaje SYN+ACK a Cliente: {new_socket.header_buffer}")
            new_socket.udp_socket.sendto(
                new_socket.header_buffer.encode(), client_address)

        else:
            print(
                "----> Recibido peticion erronea, se esperaba recibir SYN , rechazando...")

            return None

        # Recibo ACK Cliente
        new_socket.header_buffer, _ = new_socket.udp_socket.recvfrom(16)
        new_socket.header_buffer = new_socket.header_buffer.decode()
        print(
            f"----> Recibido mensaje ACK por Cliente: {new_socket.header_buffer}")

        new_socket.parsed_buffer = new_socket.parse_segment(
            new_socket.header_buffer)
        syn, ack, fin, new_seq = [int(val)
                                  for val in new_socket.header_buffer.split('|||')]
        if (syn == 0 and ack == 1 and fin == 0 and new_socket.verify_seq_3way(new_seq, new_socket.seq)):
            new_socket.seq = new_seq

            # Envio ACK (Stop & Wait)
            new_socket.header_buffer = new_socket.make_tcp_headers(
                0, 1, 0, new_socket.seq + 1)
            print(
                f"----> Enviando mensaje ACK a Cliente, paso Stop & Wait: {new_socket.header_buffer}")

            new_socket.udp_socket.sendto(
                new_socket.header_buffer.encode(), client_address)

            # Devolvemos nueva instancia de SocketTCP
            return (new_socket, new_socket.orig_address)
        else:
            print("----> Handshake erroneo, se esperaba recibir ACK, rechanzando...")

            return None

    def _send(self, message: bytes) -> None:
        """Se encarga de enviar el contenido del mensaje como tal, manejando
        adecuadamente la excepcion de timeout.
        """

        message_length = len(message)

        # Preguntamos si el largo de message es menor al buffer message
        msg_short = True if message_length <= 16 else False

        while (self.sended_data_len < message_length):
            # Recalculamos pues cambia en cada iteracion
            msg_short = True if message_length <= 16 else False

            header = self.make_tcp_headers(0, 0, 0, self.seq) + '|||'
            send_msg = header.encode()

            if msg_short:
                send_msg += message
                print(
                    f"----> Enviando mensaje a Servidor:\n{header}" + str(message))
            else:
                send_msg += message[:16]
                print(
                    f"----> Enviando mensaje a Servidor:\n{header}" + str(message[:16]))

            self.udp_socket.sendto(send_msg)

            try:  # Intentamos recibir el mensaje ACK por Servidor
                self.udp_socket.settimeout(self.timeout)
                ack_message, _ = self.udp_socket.recvfrom(16)
                ack_message = ack_message.decode()
                new_seq = self.parse_segment(ack_message)['SEQ']

                verifier_seq = self.verify_inc_seq(new_seq, self.seq)
                if (verifier_seq[0]):  # Verificamos que el numero de secuencia sea correcto
                    print(f"----> Recibido ACK por Servidor: {ack_message}")
                    self.seq = new_seq
                    # En caso de rebicir, eliminamos lo enviado
                    if (msg_short):
                        self.sended_data_len += message_length
                    else:
                        self.sended_data_len += 16
                        message = message[self.sended_data_len:]
            except socket.timeout:
                print(
                    "----> Respuesta ACK del Servidor NO RECIBIDA, intentando nuevamente")
                self._send(message[self.sended_data_len:])

    def send(self, message: bytes) -> None:
        """Envia el contenido de message a traves del socketTCP.
        """

        message_length = len(message)

        # Enviamos largo del mensaje
        header_and_content = self.make_tcp_headers(
            0, 0, 0, self.seq, message_length)
        self.udp_socket.sendto(message, self.dest_address)
        print(
            f"----> Enviando largo del mensaje a Servidor: {header_and_content}")

        try:  # Intentamos recibir el mensaje ACK por Servidor
            self.udp_socket.settimeout(5)
            ack_message, _ = self.udp_socket.recvfrom(16)
            ack_message = ack_message.decode()
            print(f"----> Recibido ACK por Servidor: {ack_message}")
        except socket.timeout:  # En caso contrario enviamos nuevamente el mensaje
            print("----> Respuesta ACK del Servidor NO RECIBIDA, intentando nuevamente")
            self.send(message)

        # Enviamos el mensaje
        self._send(message)

    def _recv(self, buff_size: int) -> None:
        """Se encarga de recibir el contenido del mensaje como tal, manejando
        adecuadamente la excepcion timeout.
        """
        ...

    def recv(self, buff_size: int) -> None:
        """Recibe un maximo buff_size de datos enviados a traves del socketTCP.
        """

        while True:
            byte_buffer, _ = self.udp_socket.recvfrom(DATA_LEN)
            header = byte_buffer.decode()
            parsed_header = self.parse_segment(header)
            # Obtenemos largo del mensaje que recibiremos
            msg_len = parsed_header['DATA']
            new_seq = parsed_header['SEQ'] + msg_len

            print(
                f"----> Recibido header con largo del mensaje que se enviara por Cliente\nLargo: {msg_len} Header: {header}")

            verifier_seq = self.verify_inc_seq(new_seq, self.seq)

            if (verifier_seq[0]):
                ack_message = self.make_tcp_headers(0, 1, 0, new_seq)
            else:
                ack_message = self.make_tcp_headers(0, 1, 0, self.seq)

            print(f"Enviando ACK confirmacion a Cliente: {ack_message}")

            self.udp_socket.sendto(ack_message.encode(), self.dest_address)

            # Si recibimos correctamente el mensaje se termina el loop,
            # si en cambio recibimos un mensaje con SEQ menor quiere decir que
            # el cliente no recibio nuestro ACK, por tanto seguimos en el loop para reenviar nuevamente ACK
            if (verifier_seq[0]):
                break

        self._send(buff_size)
