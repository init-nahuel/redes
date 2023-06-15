
class Router:
    def __init__(self):
        # Lista con las rutas no parseadas para round robin
        self.rr_routes = None

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
                    # lo de arriba puede ir fuera pues se repite

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

        decoded_packets = list(map(lambda f: (self.parse_packet(f), int(self.parse_packet(f)['offset'])), fragment_list))
        decoded_packets.sort(key=lambda t: t[1])

        if len(decoded_packets) == 1 and decoded_packets[0]['FLAG'] == 1: # Caso fragmento incompleto, descartamos
            return None
        
        if len(decoded_packets) == 1 and decoded_packets[0]['FLAG'] == 0:
            return self.create_packet(decoded_packets[0])
        
        first_element = decoded_packets[0]
        first_fragment = first_element[0]
        previous_offset = int(first_fragment['offset']) + int(first_fragment['size'])
        packet_content = first_fragment['message']

        # Creamos el posible paquete parseado que se retornara si el ensamblaje es correcto
        packet_dict = {}
        packet_dict['dest_ip'] = first_fragment['dest_ip']
        packet_dict['dest_port'] = first_fragment['dest_port']
        packet_dict['TTL'] = first_fragment['TTL']
        packet_dict['ID'] = first_fragment['ID']
        
        is_fragment = 0 # Variable para reconocer si la lista de fragmentos al ensamblarlos crea un fragmento o paquete

        size_fragments_list = len(decoded_packets)
        for i in range(1, size_fragments_list):
            fragment = decoded_packets[i]
            fragment_offset = fragment[1]
            parsed_fragment = fragment[0]

            if (fragment_offset != previous_offset): # Caso offsets no coinciden
                return None
            
            if (i == size_fragments_list - 1): # Caso iteracion llega al ultimo elemento
                is_fragment = int(parsed_fragment['FLAG'])
                packet_content += parsed_fragment['message']
                break

            packet_content += parsed_fragment['message']
            previous_offset += int(parsed_fragment['size'])

        # El offset sera nuestro offset inicial mas los largos de los fragmentos si el FLAG del ultimo fragmento
        # ensamblado es 1 y 0 en caso contrario
        packet_dict['offset'] = first_fragment['offset']
        packet_dict['size'] = self._make_size_number(len(packet_content.encode()))
        packet_dict['FLAG'] = str(is_fragment)
        packet_dict['message'] = packet_content

        return self.create_packet(packet_dict)