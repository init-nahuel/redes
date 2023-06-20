import socket
from threading import Thread
import time

t = 10


def timer() -> None:
    """Timer para timeout a la hora de llamar a `run_BGP`, utiliza la variable global
    `t` para contar el tiempo transcurrido.
    """

    global t
    while True:
        if t == 0:
            return
        else:
            time.sleep(1)
            print("Dormi")
            t -= 1


def wait(time_event, timeout):
    return time_event + timeout <= time.time()


class Router:
    def __init__(self, socket: socket.socket, router_addres: tuple[str, int]):
        # Lista con las rutas no parseadas para round robin
        self.rr_routes = None
        self.router_socket = socket
        self.router_ip = router_addres[0]
        self.router_port = router_addres[1]

    def parse_packet(self, ip_packet: bytes) -> dict[str, str]:
        """Extrae los datos del paquete IP recibido, retorna un diccionario
        con las llaves `dest_ip`: ip de destino, `dest_port`: puerto de destino, `message`: mensaje del paquete,
        `TTL`: time to live, y las llaves correspondientes a los campos de fragmentacion: `offset`, `ID`, `size` y `FLAG`.
        """

        packet_data = ip_packet.decode().split(',', 7)

        # Como viene en un orden determinado el paquete simplemente asignamos los valores
        parsed_packet = {'dest_ip': packet_data[0],
                         'dest_port': packet_data[1],
                         'TTL': packet_data[2],
                         'ID': packet_data[3],
                         'offset': packet_data[4],
                         'size': packet_data[5],
                         'FLAG': packet_data[6],
                         'message': packet_data[7]}

        return parsed_packet

    def create_packet(self, parsed_ip_packet: dict[str, str]) -> str:
        """Recibe el diccionario que retorna `parse_packet` y crea un paquete IP de acuerdo
        a la estructura definida y las llaves de este diccionario.
        """

        packet = ""
        for _, val in parsed_ip_packet.items():
            packet += val + ','

        # Eliminamos el ultimo separador sobrante
        packet = packet.strip(',')

        return packet

    def parse_route(self, route: str) -> dict[str, str | tuple[int, int] | tuple[str, int]]:
        """Extrae los datos dada una fila de la tabla de rutas, retorna un diccionario con las llaves: `red_CIDR`: direccion IP,
        `port_range`: rango de puertos y `hop_address`: siguiente salto para llegar a la red de destino.
        """

        parsed_route = {}
        route_list = route.split(' ')

        parsed_route['red_CIDR'] = route_list[0]
        parsed_route['port_range'] = (int(route_list[1]), int(route_list[2]))
        parsed_route['hop_address'] = (route_list[3], int(route_list[4]))
        parsed_route['MTU'] = route_list[5]

        return parsed_route

    def check_routes(self, routes_file_name: str, destination_address: tuple[str, int]) -> tuple[tuple[str, int], int] | None:
        """Revisa en orden descendente la tabla de rutas guardada en el archivo `routes_file_name`, en caso de existir
        una ruta apropiada en la tabla de rutas, se retorna la tupla ((IP, puerto),mtu) con la direccion de salto siguiente en la red y el mtu
        de la ruta seleccionada, en caso contrario retorna `None`.
        """
        try:
            with open(routes_file_name, "r") as f:
                routes = f.read()
                raw_routes = routes.split('\n')

                # Agregamos la lista de rutas completas solo al comienzo o si esta se encuentra vacia (caso router con una ruta)
                if (self.rr_routes == None or len(self.rr_routes) == 0):
                    self.rr_routes = raw_routes

                for r in self.rr_routes:
                    parsed_route = self.parse_route(r)
                    min_port = parsed_route['port_range'][0]
                    max_port = parsed_route['port_range'][1]
                    mtu = parsed_route['MTU']

                    if (parsed_route['red_CIDR'] == destination_address[0] and min_port <= destination_address[1] <= max_port):
                        # La removemos y agregamos al final, como se recorre en secuencia la lista de rutas se
                        # asegura que la ruta utilizada ahora no se utilizara denuevo hasta que las rutas alternativas se usen y se agregen
                        # despues de esta (si es que existen rutas alternativas)
                        self.rr_routes.remove(r)
                        self.rr_routes.append(r)

                        return (parsed_route['hop_address'], int(mtu))
                return None
        except OSError:
            print("----> Archivo tabla de rutas corrompido, no es posible leerlo.")

    def check_ttl(self, parsed_packet: dict[str, str]) -> bool:
        """Retorna `True` si la llave `TTL` del diccionario (paquete parseado) es mayor a 0 y adicionalmente decrementa este
        valor en 1, retorna `False` en caso contrario.
        """

        if (parsed_packet['TTL'] == 0):
            return False
        else:
            parsed_packet['TTL'] = str(int(parsed_packet['TTL']) - 1)
            return True

    def _get_header(self, ip_packet: bytes) -> tuple[bytes, bytes]:
        """Retorna una tupla donde el primer elemento es el header del paquete IP y el
        segundo elemento es el mensaje del respectivo paquete."""

        parsed_packet = self.parse_packet(ip_packet)
        packet_content = parsed_packet['message']

        packet_header = ""
        for key, val in parsed_packet.items():
            if key == 'message':
                continue
            packet_header += val + ','
        # Notar que el header terminara con una ',' esto es asi pues despues se concateno el mensaje del paquete

        return (packet_header.encode(), packet_content.encode())

    def _parse_header(self, header_packet: bytes) -> dict[str, str]:
        """Retorna un diccionario con el header del paquete parseado, es decir, el diccionario contiene
        las llaves `dest_ip`, `dest_port`, `TTL`, `ID`, `offset`, `size`, `FLAG`.
        """

        packet_data = header_packet.decode().split(',', 7)

        parsed_packet = {'dest_ip': packet_data[0],
                         'dest_port': packet_data[1],
                         'TTL': packet_data[2],
                         'ID': packet_data[3],
                         'offset': packet_data[4],
                         'size': packet_data[5],
                         'FLAG': packet_data[6]}

        return parsed_packet

    def _make_size_number(self, n: int) -> str:
        """Retorna el numero `n` en el formato definido, i.e. un string de 8 digitos. Ej: n=34 -> '00000043'
        """

        str_len = len(str(n))

        return "0"*(8 - str_len) + str(n)

    def fragment_IP_packet(self, ip_packet: bytes, mtu: int) -> list[bytes]:
        """Retorna una lista de fragmentos cuyo largo es mayor o igual a uno, estos fragmentos
        tendran un tamanho menor o igual a `mtu`.
        """

        if (len(ip_packet) <= mtu):
            return [ip_packet]
        else:
            packet_header, packet_msg = self._get_header(ip_packet)
            coded_header_size = len(packet_header)
            parsed_header = self._parse_header(packet_header)
            is_fragment = int(parsed_header['FLAG'])

            # Consideramos el offset del fragmento original para los fragmentos de este en caso de FLAG = 1
            offset = int(parsed_header['offset'])

            # Asignamos FLAG=1 para los fragmentos
            parsed_header['FLAG'] = str(1)
            fragments_list = []
            while (True):
                # Debemos tener cuidado pues en cada iteracion se modifica el diccionario parsed_header, por eso se guarda en una variable al comienzo
                # el valor de FLAG (is_fragment)
                if (len(packet_msg) <= mtu - coded_header_size):
                    # Convertimos el header parseado a un paquete como tal agregando la llave message
                    parsed_header['message'] = packet_msg.decode()
                    parsed_header['offset'] = str(offset)
                    parsed_header['size'] = self._make_size_number(
                        len(packet_msg))
                    parsed_header['FLAG'] = str(1) if is_fragment else str(0)

                    fragments_list.append(
                        self.create_packet(parsed_header).encode())
                    break

                content_size = len(packet_msg[0:mtu-coded_header_size])
                parsed_header['size'] = self._make_size_number(content_size)
                parsed_header['offset'] = str(offset)
                parsed_header['message'] = packet_msg[0:mtu -
                                                      coded_header_size].decode()

                fragments_list.append(
                    self.create_packet(parsed_header).encode())
                packet_msg = packet_msg[mtu-coded_header_size:]
                offset += content_size

            return fragments_list

    def reassemble_IP_packet(self, fragment_list: list[bytes]) -> str | None:
        """Reensambla un paquete IP a partir de una lista de fragmentos `fragment_list` y retorna el paquete, en caso de que
        la lista se encuentre incompleta se retorna `None`.
        """

        # Creamos una lista ordenada segun offset de tuplas (fragmento parseado, offset)
        decoded_fragments = list(map(lambda f: (self.parse_packet(
            f), int(self.parse_packet(f)['offset'])), fragment_list))
        decoded_fragments.sort(key=lambda t: t[1])

        size_fragments_list = len(decoded_fragments)

        first_element = decoded_fragments[0]
        first_fragment = first_element[0]
        offset = int(
            first_fragment['offset']) + int(first_fragment['size'])
        packet_content = first_fragment['message']
        flag_first_fragment = int(first_fragment['FLAG'])

        # Caso tenemos solo un fragmento, todavia falta recibir mas
        if size_fragments_list == 1 and flag_first_fragment == 1:
            return None

        if size_fragments_list == 1 and flag_first_fragment == 0:
            return self.create_packet(first_fragment)

        # Creamos el posible paquete parseado que se retornara si el ensamblaje es correcto
        packet_dict = {}
        packet_dict['dest_ip'] = first_fragment['dest_ip']
        packet_dict['dest_port'] = first_fragment['dest_port']
        packet_dict['TTL'] = first_fragment['TTL']
        packet_dict['ID'] = first_fragment['ID']
        packet_dict['offset'] = first_fragment['offset']

        # Variable para reconocer si la lista de fragmentos al ensamblarlos crea un fragmento o paquete
        is_fragment: int

        for i in range(1, size_fragments_list):
            fragment = decoded_fragments[i]
            fragment_offset = fragment[1]
            parsed_fragment = fragment[0]

            if (fragment_offset != offset):  # Caso offsets no coinciden
                return None

            if (i == size_fragments_list - 1):  # Caso iteracion llega al ultimo elemento
                is_fragment = int(parsed_fragment['FLAG'])
                packet_content += parsed_fragment['message']
                break

            packet_content += parsed_fragment['message']
            offset += int(parsed_fragment['size'])

        packet_dict['size'] = self._make_size_number(
            len(packet_content.encode()))
        packet_dict['FLAG'] = str(is_fragment)
        packet_dict['message'] = packet_content

        return self.create_packet(packet_dict)

    def receiver_manager(self, packets_dict: dict[str, list[bytes]], parsed_fragment: dict[str, str], packet_buffer: bytes) -> str | None:
        """Almacena el fragmento `packet_buffer` en el diccionario `packets_dict` segun el ID del 
        fragmento, en cada llamada trata de reensamblar el paquete segun el fragmento recibido, en caso de reensamblarlo
        retorna el paquete reensamblado, en caso contrario retorna `None`.
        """

        fragment_id = parsed_fragment['ID']

        if fragment_id not in packets_dict.keys():
            packets_dict[fragment_id] = [packet_buffer]
            poss_assem_packet = self.reassemble_IP_packet(
                packets_dict[fragment_id])

            if poss_assem_packet is not None:
                packets_dict.pop(fragment_id)
                return poss_assem_packet
            else:
                return None

        packets_dict[fragment_id].append(packet_buffer)
        poss_assem_packet = self.reassemble_IP_packet(
            packets_dict[fragment_id])

        if poss_assem_packet is not None:
            parsed_assem_packet = self.parse_packet(poss_assem_packet.encode())

            # Caso: el paquete reensamblado posee FLAG=1 -> reensamblamos un fragmento, todavia falta
            if int(parsed_assem_packet['FLAG']) == 1:
                packets_dict[fragment_id] = [poss_assem_packet.encode()]
                return None
            else:
                packets_dict.pop(fragment_id)
                return poss_assem_packet

        return None


class BGP:
    def __init__(self, router: Router, routes_file_path: str) -> None:
        self.router: Router = router

        # Lista con los ASN de los routers conocidos por el routes asociado
        self.known_asns: list[str] = []

        self.routes_file: str = routes_file_path  # Tabla de rutas del router asociado
        self.neighbour_ports: list[int] = []  # Vecinos del router asociado

    def _get_asn_route(self, route: str) -> str:
        """Obtiene la ruta ASN que contiene la ruta `route`, retorna un string con la ruta.
        Ej: '127.0.0.1 8882 8881 127.0.0.1 8882 100' -> '8882 8881'.
        """

        # Dividimos empezando desde la derecha una cantidad de 3 espacios y
        # luego uno desde la izquierda, esto funciona debido al formato estandar que se definio
        route = route.rsplit(' ', 3)

        route = route[0].split(' ', 1)
        asn_route = route[1]  # Obtenemos la ruta ASN

        return asn_route

    def _get_neighbours(self) -> None:
        """Obtiene los puertos de los routers vecinos al router asociado y los guarda en `self.neighbour_ports`.
        """

        with open(self.routes_file, "r") as f:
            routes_list = f.read().split("\n")

            for route in routes_list:
                port = int(route.rsplit(' ', 2)[-2])
                self.neighbour_ports.append(port)
                self.known_asns.append(str(port))

        return None

    def _send_bgp_msg(self, router_socket: socket.socket, msg_type: str) -> None:
        """Envia los mensajes de tipo `msg_type` a los routers vecinos del router asociado
        a traves del socket `router_socket`.
        """

        if msg_type == "BGP_ROUTES":
            for port in self.neighbour_ports:
                bgp_routes_packet = self.create_BGP_message(
                    self.routes_file, '127.0.0.1', port, 10, 120)
                router_socket.sendto(
                    bgp_routes_packet.encode(), ('localhost', port))
        elif msg_type == "START_BGP":
            for port in self.neighbour_ports:
                bgp_start_packet = self.create_init_BGP_message(
                    '127.0.0.1', port, 10, 120)
                router_socket.sendto(
                    bgp_start_packet.encode(), ('localhost', port))

        return None

    def _parse_bgp_routes(self, msg: str) -> dict[str, str | list[str]]:
        """Parsea el mensaje BGP_ROUTES y entrega un diccionario con las llaves: `router_ASN`: ASN del router que envio el paquete, 
        `ASN_routes`: lista con las rutas ASN contenidas en el mensaje.
        """

        msg_dict = {}
        msg = msg.split('\n')
        msg_dict['router_ASN'] = msg[1]
        msg_dict['ASN_routes'] = []

        for i in range(2, len(msg)-1):
            msg_dict['ASN_routes'].append(msg[i])

        return msg_dict

    def _create_new_route(self, asn_route: list[str]) -> str:
        """Retorna una nueva ruta para agregar en la tabla de rutas dada una ruta ASN en forma de lista con los ASN.
        """

        new_route = "127.0.0.1 "

        for asn in asn_route:
            new_route += asn + " "

        new_route += "{} ".format(self.router.router_port)

        new_route += "127.0.0.1 {} 100".format(asn_route[-1])

        return new_route

    def _search_coincidende_asn_route(self, routes_table: str, dest_asn: str) -> tuple[str, str]:
        """Busca en la tabla de rutas `routes_table` la ruta que coincide con el ASN de destino `dest_asn`, retorna
        una tupla con la tabla de rutas nueva con la ruta que coincide eliminada
        y la ruta eliminada.
        """

        raw_routes_list = routes_table.split('\n')

        for raw_route in raw_routes_list:
            # Dado el formato de rutas podemos obtener asi el ASN de destino
            route_dest_asn = raw_route.split(' ', 2)[1]

            if route_dest_asn == dest_asn:
                raw_routes_list.remove(raw_route)
                break

        return ('\n'.join(raw_routes_list), raw_route)

    def create_init_BGP_message(self, dest_ip: str, dest_port: int, ttl: int, id: int) -> str:
        """Crea el paquete con el mensaje de inicio del algoritmo BGP `START_BGP`.
        """

        packet_dict = {'dest_ip': str(dest_ip),
                       'dest_port': str(dest_port),
                       'TTL': str(ttl),
                       'ID': str(id),
                       'offset': "0",
                       'size': str(len("START_BGP".encode())),
                       'FLAG': "0",
                       'message': "START_BGP"}
        start_bgp_packet = self.router.create_packet(packet_dict)

        return start_bgp_packet

    def create_BGP_message(self, routes_file_name: str, dest_ip: str, dest_port: int, ttl: int, id: int) -> str:
        """Crea un mensage con rutas BGP `BGRP_ROUTES` para lo cual lee el archivo `routes_file_name` con las rutas del router asociado.
        """

        packet_dict = {'dest_ip': str(dest_ip),
                       'dest_port': str(dest_port),
                       'TTL': str(ttl),
                       'ID': str(id),
                       'offset': "0"}

        content = 'BGP_ROUTES\n{}'.format(dest_port)
        with open(routes_file_name, "r") as f:
            routes_list = f.read().split("\n")

            for r in routes_list:
                asn_route = self._get_asn_route(r)
                content += '\n{}'.format(asn_route)

        packet_dict['size'] = str(len(content.encode()))
        packet_dict['FLAG'] = "0"
        packet_dict['message'] = content + "\nEND_BGP_ROUTES"
        bgp_routes_packet = self.router.create_packet(packet_dict)

        return bgp_routes_packet

    def run_BGP(self) -> str:
        """Se encarga de ejecutar el protoclo de ruteo BGP, retorna un string con la tabla de rutas
        del router asociado.
        """

        router_socket = self.router.router_socket

        # Enviamos el mensaje START_BGP a nuestros vecinos
        self._get_neighbours()  # Guardamos los vecinos del router en self.neighbour_ports
        print("----> Enviando mensaje START_BGP a routers vecinos")
        self._send_bgp_msg(router_socket, "START_BGP")

        prev_route_table = ""
        with open(self.routes_file, "r") as f:
            current_route_table = f.read()
        prev_route_table = current_route_table

        # Inicialmente enviamos las rutas a nuestros vecinos
        print("----> Enviando mensaje BGP_ROUTES")
        self._send_bgp_msg(router_socket, "BGP_ROUTES")

        while True:
            # Caso tabla de rutas cambia -> reset timer y envio nuevamente rutas
            if prev_route_table != current_route_table:
                prev_route_table = current_route_table

                # Modificamos el archivo de tablas de rutas
                with open(self.routes_file, "w") as f:
                    f.write(current_route_table)

                print(
                    "----> Se modificaron las tablas de rutas, enviando mensaje BGP_ROUTES a routers vecinos")
                self._send_bgp_msg(router_socket, "BGP_ROUTES")

            try:
                # Esperamos recibiendo BGP_ROUTES
                self.router.router_socket.settimeout(
                    10)

                received_packet, _ = router_socket.recvfrom(1024)
                parsed_packet = self.router.parse_packet(received_packet)

                # Caso recibimos START_BGP -> ignoramos
                if "START_BGP" in parsed_packet['message']:
                    continue

                # print(
                #     f"----> Llego mensaje BGP_ROUTES: {received_packet.decode()}")
                print("----> Llego mensaje BGP_ROUTES")

                # Sino estamos recibiendo rutas por tanto revisamos si sirven
                parsed_bgp_routes = self._parse_bgp_routes(
                    parsed_packet['message'])

                new_routes = ""
                for route in parsed_bgp_routes['ASN_routes']:

                    # Caso ruta contiene el ASN del router asociado -> descartamos
                    if str(self.router.router_port) in route:
                        continue

                    # Generamos una lista con los ASN de la nueva ruta ASN
                    asn_route_parsed = route.split(' ')

                    dest_asn = asn_route_parsed[0]

                    # Caso no conocemos el ASN de destino -> agregamos la ruta
                    if dest_asn not in self.known_asns:
                        self.known_asns.append(dest_asn)
                        new_routes += "\n" + \
                            self._create_new_route(asn_route_parsed)
                    else:  # Caso conocemos el ASN de destino -> comparamos
                        new_route_table, asn_route = self._search_coincidende_asn_route(
                            current_route_table, dest_asn)
                        asn_route = self._get_asn_route(asn_route).split(' ')

                        # Caso ruta nueva es mas corta -> reemplazamos
                        if len(asn_route) > len(asn_route_parsed):
                            current_route_table = new_route_table
                            new_routes += "\n" + \
                                self._create_new_route(asn_route_parsed)

                if new_routes != "":  # Agregamos nuevas rutas
                    current_route_table += new_routes
                    # Caso sacamos una ruta para comparar cual era mas corta y gano la ruta previa
                    # if len(current_route_table) == len(new_routes) + len(prev_route_table):
                    #     current_route_table = prev_route_table
                    # else:
                    #     current_route_table += new_routes
            except socket.timeout:
                # Volvemos a resetear al valor por default el timeout del socket
                self.router.router_socket.settimeout(None)
                break

        print("----> Finalizando ejecucion algoritmo BGP")
        return current_route_table
