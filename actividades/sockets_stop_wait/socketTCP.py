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
        self.content_buffer = bytes()

        # Data restante que se recibe el socket cuando buff_size es menor que 16 bytes
        self.remaining_data = bytes()

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
        return (diff >= 0, diff)

    @staticmethod
    def is_valid_header(parsed_header: dict[str, str], syn: int, ack: int, fin: int) -> bool:
        """Retorna True si el header parseado parsed_header posee las flags syn, ack, fin activa o desactivada.
        Retorna False caso contrario.
        """

        return syn == int(parsed_header['SYN']) and ack == int(parsed_header['ACK']) and fin == int(parsed_header['FIN'])

    def _manage_timeout(self):
        """Maneja el recibo de mensajes ACK desde Servidor, en caso de no recibir lanza nuevamente
        la excepcion socket.timeout.
        """

        try:
            self.udp_socket.settimeout(self.timeout)
            ack_msg, _ = self.udp_socket.recvfrom(16)
            ack_msg = ack_msg.decode()
            new_seq = int(self.parse_segment(ack_msg)['SEQ'])
            self.seq = new_seq
            print(f"----> Recibido ACK por Servidor: {ack_msg}")
        except socket.timeout:
            print(
                f"----> No se recibio respuesta del servidor durante el timeout: {self.timeout}, intentando nuevamente")
            raise socket.timeout

    def bind(self, address: tuple[str, int]):
        """Aisgna una direccion de origen (IP, Puerto) al socket SocketTCP.
        """

        self.orig_address = address
        self.udp_socket.bind(address)

    def connect(self, address) -> int:
        """Establece el 3-way handshake entre el socket SocketTCP cliente y
        el servidor ubicado en la direccion de destino address
        en la que se encuentra escuchando. Retorna 1 en caso de establecerse correctamente
        el handshake y 0 en caso contrario.
        """

        self.seq = random.randint(0, 100)
        self.dest_address = address

        # 3-way handshake

        # Envio mensaje SYN Cliente
        self.header_buffer = self.make_tcp_headers(1, 0, 0, self.seq)

        print(
            f"----> Enviando mensaje SYN a Servidor: {self.header_buffer}")

        while True:
            # Enviamos el SYN dentro del loop pues en caso de que este se pierda, no recibiremos respuesta de Servidor.
            # Asimismo si se pierde la respuesta pero el SYN llega aun asi deberemos enviarlo nuevamente para notificar al Servidor (y el manejara la respuesta)
            self.udp_socket.sendto(
                self.header_buffer.encode(), self.dest_address)
            try:
                # Recibo SYN+ACK Servidor
                self.udp_socket.settimeout(self.timeout)
                self.header_buffer, new_socket_address = self.udp_socket.recvfrom(
                    16)
                self.header_buffer = self.header_buffer.decode()
                print(
                    f"----> Recibido mensaje SYN+ACK desde Servidor: {self.header_buffer}")

                self.dest_address = new_socket_address
                self.parsed_buffer = self.parse_segment(self.header_buffer)
                new_seq = int(self.parsed_buffer['SEQ'])

                # En verify_seq_3way sumamos 1 pues en el primer SYN del Cliente va el SEQ sin incremento
                if (self.verify_seq_3way(new_seq + 1, self.seq) and self.is_valid_header(self.parsed_buffer, 1, 1, 0)):
                    self.seq = new_seq
                    break
                else:
                    print(f"----> Header invalido, cancelando conexion...")

                    return 0
            except socket.timeout:
                print(
                    f"----> No se recibio respuesta del servidor durante el timeout: {self.timeout}, intentando nuevamente")
                continue

        while True:  # Caso recibimos el SYN+ACK correctamente, seguimos ahora enviando el ACK
            # Envio ACK Cliente
            self.header_buffer = self.make_tcp_headers(0, 1, 0, self.seq + 1)

            print(
                f"----> Enviando mensaje ACK de confirmacion a Servidor: {self.header_buffer}")
            self.udp_socket.sendto(
                self.header_buffer.encode(), self.dest_address)

            try:
                # Recibo ACK Servidor (Stop & Wait)
                self.header_buffer, _ = self.udp_socket.recvfrom(16)
                self.header_buffer = self.header_buffer.decode()
                print(
                    f"----> Recibido mensaje ACK por Servidor, paso Stop & Wait: {self.header_buffer}")

                self.parsed_buffer = self.parse_segment(self.header_buffer)
                new_seq = int(self.parsed_buffer['SEQ'])
                if (self.verify_seq_3way(new_seq, self.seq) and self.is_valid_header(self.parsed_buffer, 0, 1, 0)):
                    self.seq = new_seq

                    return 1
                else:
                    print(f"----> Header invalido, cancelando conexion...")

                    return 0
            except socket.timeout:
                print(
                    f"----> No se recibio respuesta del servidor durante el timeout: {self.timeout}, intentando nuevamente")
                continue

    def accept(self) -> tuple[SocketTCP, tuple[str, int]] | None:
        """Establece el 3-way handshake entre el socket SocketTCP Servidor y el cliente.
        Retorna una tupla con un nuevo socket SocketTCP y la direccion de este nuevo socket."""

        # Creamos el nuevo socket para el
        new_socket = SocketTCP()

        # 3-way handshake
        # Recibo SYN Cliente
        new_socket.header_buffer, client_address = self.udp_socket.recvfrom(16)
        new_socket.dest_address = client_address

        new_socket.header_buffer = new_socket.header_buffer.decode()
        print(
            f"----> Recibido mensaje SYN por Cliente: {new_socket.header_buffer}")

        new_socket.parsed_buffer = new_socket.parse_segment(
            new_socket.header_buffer)
        new_socket.seq = int(new_socket.parsed_buffer['SEQ'])

        if (self.is_valid_header(new_socket.parsed_buffer, 1, 0, 0)):
            new_socket.header_buffer = new_socket.make_tcp_headers(
                1, 1, 0, new_socket.seq + 1)

            # Envio SYN+ACK
            print(
                f"----> Enviando mensaje SYN+ACK a Cliente: {new_socket.header_buffer}")
            new_socket.udp_socket.sendto(
                new_socket.header_buffer.encode(), new_socket.dest_address)

        else:
            print(
                "----> Recibido peticion erronea, se esperaba recibir SYN , rechazando...")

            return None

        # Recibo ACK Cliente
        while True:
            new_socket.header_buffer, _ = new_socket.udp_socket.recvfrom(16)
            new_socket.header_buffer = new_socket.header_buffer.decode()

            new_socket.parsed_buffer = new_socket.parse_segment(
                new_socket.header_buffer)
            new_seq = int(new_socket.parsed_buffer['SEQ'])

            if (self.is_valid_header(new_socket.parsed_buffer, 0, 1, 0) and new_socket.verify_seq_3way(new_seq, new_socket.seq)):
                print(
                    f"----> Recibido mensaje ACK por Cliente: {new_socket.header_buffer}")
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
            elif (self.is_valid_header(self.parsed_buffer, 1, 0, 0)):
                # Caso nos llega nuevamente el mensaje SYN de Cliente -> no llego nuestro SYN+ACK
                new_socket.header_buffer = new_socket.make_tcp_headers(
                    1, 1, 0, new_socket.seq + 1)

                print(
                    f"----> Enviando nuevamente SYN+ACK, no recibido por Cliente probablemente: {new_socket.header_buffer}")
                new_socket.udp_socket.sendto(
                    new_socket.header_buffer.encode(), new_socket.dest_address)
                continue
            else:
                print("----> Handshake erroneo, se esperaba recibir ACK, rechazando...")

                return None

    def _send(self, message: bytes) -> None:
        """Se encarga de enviar el contenido del mensaje como tal, manejando
        adecuadamente la excepcion de timeout.
        """

        self.sended_data_len = len(message)
        while (self.readed_data_len < self.sended_data_len):
            header = self.make_tcp_headers(0, 0, 0, self.seq) + '|||'
            send_msg = header.encode()
            content = message[self.readed_data_len:self.readed_data_len +
                              min(self.sended_data_len - self.readed_data_len, 16)]
            send_msg += content

            self.udp_socket.sendto(send_msg, self.dest_address)

            print(f"----> Enviando mensaje a Servidor, Contenido: {content}")

            try:
                self._manage_timeout()
                self.readed_data_len += min(self.sended_data_len -
                                            self.readed_data_len, 16)
            except socket.timeout:
                # self._send(message)
                # Deberia funcionar continue pues al final todo depende de self.readed_data_len, este no cambia si lanza excepcion
                continue

        return None

    def send(self, message: bytes) -> None:
        """Envia el contenido de message a traves del socketTCP.
        """

        message_length = len(message)

        # Establecemos el largo que debe leer (y lo que ha leido) y enviar el socket
        self.sended_data_len = message_length
        self.readed_data_len = 0

        # Enviamos largo del mensaje
        header_and_len_msg = self.make_tcp_headers(
            0, 0, 0, self.seq, message_length)
        self.udp_socket.sendto(header_and_len_msg.encode(), self.dest_address)
        print(
            f"----> Enviando largo del mensaje a Servidor: {header_and_len_msg}")

        try:  # Intentamos recibir el mensaje ACK por Servidor
            self._manage_timeout()
        except socket.timeout:  # En caso contrario enviamos nuevamente el mensaje
            self.send(message)

        # Enviamos el mensaje
        self._send(message)

    def _recv(self, buff_size: int) -> None:
        """Se encarga de recibir el contenido del mensaje como tal, manejando
        adecuadamente la recepcion de mensajes duplicados.
        """

        min_value = min(self.sended_data_len - self.readed_data_len, buff_size)

        # Vaciamos el buffer en caso de que se esta llamando recv para recibir un mensaje nuevo
        self.content_buffer = bytes()

        while (self.readed_data_len != min_value):

            if (self.readed_data_len == self.sended_data_len):  # Caso leimos todo lo que se envio
                break

            # Calculo largo header, puede variar debido al largo del numero SEQ
            header_len = 15 + int(len(str(self.seq)))

            # Recibo los 16 bytes fijo que envia el emisor
            buffer_recv, _ = self.udp_socket.recvfrom(16 + header_len)
            parsed_header = self.parse_segment(
                buffer_recv[:header_len].decode())
            new_seq = int(parsed_header['SEQ'])

            if (self.seq == new_seq):
                recv_data = buffer_recv[header_len:]
                len_recv_data = len(recv_data)
                len_rem_data = len(self.remaining_data)
                if (len_recv_data + len_rem_data <= buff_size):
                    self.content_buffer += self.remaining_data + recv_data

                    # Reseteamos el buffer de bytes restantes
                    self.remaining_data = bytes()

                    len_readed = len_recv_data + len_rem_data
                    self.readed_data_len += len_readed
                    # Incrementamos SEQ por el contenido leido
                    self.seq += len_readed
                else:  # len_recv_data + len_rem_data > buff_size
                    # Existen dos casos posibles
                    if (len_rem_data >= buff_size):
                        self.content_buffer += self.remaining_data[:buff_size]
                        self.remaining_data = self.remaining_data[buff_size:] + recv_data
                        self.readed_data_len += buff_size
                        self.seq += buff_size
                    else:  # len_recv_data + len_rem_data > buff_size
                        self.content_buffer += self.remaining_data + \
                            recv_data[:buff_size-len_rem_data]
                        self.remaining_data = recv_data[buff_size -
                                                        len_rem_data:]
                        self.readed_data_len += buff_size
                        self.seq += buff_size

                ack_header = self.make_tcp_headers(0, 1, 0, self.seq)

                print(f"----> Recibido mensaje Cliente: {self.content_buffer}")

                print(f"----> Enviando ACK a Cliente: {ack_header}")

                self.udp_socket.sendto(ack_header.encode(), self.dest_address)
            else:  # Caso recibimos mensaje repetido (no llego ACK al cliente)
                ack_header = self.make_tcp_headers(0, 1, 0, self.seq)

                print(
                    f"----> Mensaje repetido recibido desde Cliente, probablemente ultimo ACK perdido, reenviando: {ack_header}")

                self.udp_socket.sendto(ack_header.encode(), self.dest_address)

        return None

    def recv(self, buff_size: int) -> None:
        """Recibe un maximo buff_size de datos enviados a traves del socketTCP.
        """

        while True:
            # Caso en que se llama a recv pero todavia no se ha recibido el mensaje completo
            if (self.sended_data_len - self.readed_data_len > 0):
                break

            byte_buffer, _ = self.udp_socket.recvfrom(DATA_LEN)
            header = byte_buffer.decode()
            parsed_header = self.parse_segment(header)
            # Obtenemos largo del mensaje que recibiremos
            msg_len = int(parsed_header['DATA'])
            new_seq = int(parsed_header['SEQ'])

            print(
                f"----> Recibido header con largo del mensaje que se enviara por Cliente\nLargo: {msg_len} Header: {header}")

            verifier_seq = self.verify_inc_seq(new_seq, self.seq)

            # Caso en que el SEQ recibido es mayor, modificamos nuestro SEQ
            if (verifier_seq[0]):
                self.seq = new_seq + msg_len
                self.sended_data_len = msg_len
                # Reseteamos el valor en caso de haber llamado send anteriormente
                self.readed_data_len = 0

            # Enviamos el header con el ACK y nuestro SEQ, ya sea que el Cliente no recibio el anterior
            # o si lo recibio, el cambio del SEQ del Servidor se encuentra en el if de arriba
            ack_message = self.make_tcp_headers(0, 1, 0, self.seq)
            print(f"Enviando ACK confirmacion a Cliente: {ack_message}")

            self.udp_socket.sendto(ack_message.encode(), self.dest_address)

            # Si recibimos correctamente el mensaje se termina el loop,
            # si en cambio recibimos un mensaje con SEQ menor quiere decir que
            # el cliente no recibio nuestro ACK, por tanto seguimos en el loop para reenviar nuevamente ACK
            if (verifier_seq[0]):
                break

        # Recibimos el mensaje del Cliente como tal
        self._recv(buff_size)

        return self.content_buffer

    def close(self) -> None:
        """Comienza el cierre de conexion.
        """

        # Enviamos mensaje FIN
        fin_header = self.make_tcp_headers(0, 0, 1, self.seq)
        self.udp_socket.sendto(fin_header.encode(), self.dest_address)

        print(f"----> Enviando mensaje FIN a la otra parte: {fin_header}")

        # Recibimos mensaje FIN+ACK
        ack_msg, _ = self.udp_socket.recvfrom(16)
        ack_msg = ack_msg.decode()
        parsed_ack = self.parse_segment(ack_msg)
        new_seq = int(parsed_ack['SEQ'])

        if (new_seq - self.seq == 1 and self.is_valid_header(parsed_ack, 0, 1, 1)):
            self.seq = new_seq
            ack_msg = self.make_tcp_headers(0, 1, 0, self.seq + 1)

            print(f"----> Recibido mensaje FIN+ACK: {ack_msg}")

            self.udp_socket.sendto(ack_msg.encode(), self.dest_address)

            print(f"----> Enviando mensaje ACK a la otra parte: {ack_msg}")
        else:
            print(f"----> Numeros de secuencias erroneos.")

            return None

        print(f"----> Finalizo la comunicacion")
        self.udp_socket.close()

        return None

    def recv_close(self):
        """"Continua el cierre de conexion, comenzado por la otra parte de la comunicacion.
        """

        # Recibimos mensaje FIN

        fin_msg, _ = self.udp_socket.recvfrom(16)
        fin_msg = fin_msg.decode()
        parsed_fin = self.parse_segment(fin_msg)
        fin_seq = int(parsed_fin['SEQ'])

        if (fin_seq == self.seq and self.is_valid_header(parsed_fin, 0, 0, 1)):

            print(f"----> Recibido mensaje de FIN: {fin_msg}")

            # Envio mensaje FIN+ACK
            fin_ack_msg = self.make_tcp_headers(0, 1, 1, self.seq + 1)
            self.udp_socket.sendto(fin_ack_msg.encode(), self.dest_address)

            print(f"----> Enviando mensaje FIN+ACK: {fin_ack_msg}")

            # Recibo mensaje ACK
            ack_msg, _ = self.udp_socket.recvfrom(16)
            ack_msg = ack_msg.decode()
            parsed_ack = self.parse_segment(ack_msg)
            new_seq = int(parsed_ack['SEQ'])

            if (self.verify_seq_3way(new_seq, self.seq) and self.is_valid_header(parsed_ack, 0, 1, 0)):

                print(f"----> Recibido mensaje ACK: {ack_msg}")

                self.seq = None
                print(f"----> Finalizo la comunicacion")
                self.udp_socket.close()

                return None

            else:
                print(f"----> Numeros de secuencias erroneos.")
                return None

        else:
            print(f"----> Numeros de secuencias erroneos.")
            return None
