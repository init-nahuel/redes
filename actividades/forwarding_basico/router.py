import socket


class Router:
    def __init__(self, router_socket: socket.socket, router_address: tuple[str, int], router_routes: str):
        self.router_socket = router_socket
        self.router_address = router_address
        self.router_ip = router_address[0]
        self.router_port = int(router_address[1])
        self.router_routes = router_routes

    def parse_packet(self, ip_packet: bytes) -> dict[str, str]:
        """Extrae los headers datos del paquete IP recibido, retorna un diccionario
        con las llaves `dest_ip`: ip de destino, `dest_port`: puerto de destino
        y `message`: mensaje del paquete.
        """

        packet_data = ip_packet.decode().split(',')

        # Se utiliza replace para hacer formatting del dato obtenido, segun el estandar
        # definido esto no es necesario pues los paquetes debiesen encontrarse de la siguiente manera
        # Ej: ip,port,message . Sin embargo, se realiza en caso de error.
        parsed_packet = {'dest_ip': packet_data[0].replace(' ', ''),
                         'dest_port': packet_data[1].replace(' ', ''),
                         'message': packet_data[2].replace(' ', '')}

        return parsed_packet

    def create_packet(self, parsed_ip_packet: dict[str, str]) -> str:
        """Recibe el diccionario que retorna `parse_packet` y crea un paquete IP de acuerdo
        a la estructura definida, el paquete se retorna como un string.
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

        return parsed_route

    def check_routes(self, routes_file_name: str, destination_address: tuple[str, int]) -> tuple[str, int] | None:
        """Revisa en orden descendente la tabla de rutas guardada en el archivo `routes_file_name`, en caso de existir
        una ruta apropiada en la tabla de rutas, se retorna la tupla (IP, puerto) con la direccion de salto siguiente en la red,
        en caso contrario retorna `None`.
        """
        try:
            with open(routes_file_name, "r") as f:
                routes = f.read()
                raw_routes = routes.split('\n')
                for r in raw_routes:
                    parsed_route = self.parse_route(r)
                    min_port = parsed_route['port_range'][0]
                    max_port = parsed_route['port_range'][1]

                    if (parsed_route['red_CIDR'] == destination_address[0] and min_port <= destination_address[1] <= max_port):
                        return (parsed_route['hop_address'])
        except OSError:
            print("----> Archivo tabla de rutas corrompido, no es posible leerlo.")

        return None
