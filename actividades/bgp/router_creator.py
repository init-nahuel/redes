import router
import socket
import sys


def main():
    _, router_ip, router_port, routes_filepath = sys.argv

    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    router_address = (router_ip, int(router_port))

    socket_router.bind(router_address)

    new_router = router.Router()

    router_packets: dict[str, list[bytes]] = {}

    print(f"----> La IP del router es: {router_ip}")
    print(f"----> El puerto del router es: {router_port}")
    print(f"----> Mostrando archivo con rutas:")
    with open(routes_filepath, "r") as f:
        print(f.read())
    print("<------------------------------------>")

    while True:
        buffer, _ = socket_router.recvfrom(1026)
        parsed_packet = new_router.parse_packet(buffer)
        dest_address = (parsed_packet['dest_ip'],
                        int(parsed_packet['dest_port']))

        if (dest_address == router_address):

            packet = new_router.receiver_manager(
                router_packets, parsed_packet, buffer)

            print("----> Recibido fragmento")

            if packet is not None:
                packet_content = new_router.parse_packet(packet.encode())

                if "START_BGP" in packet_content['message']:
                    print(
                        f"----> Llego el siguiente paquete: {buffer.decode()}\n----> Comenzando ruteo BGP")
                elif "BGP_ROUTES" in packet_content['message']:
                    ...
                else:
                    print(
                        f"----> Se ensamblo el siguiente paquete ({buffer.decode()}), mostrando contenido: {packet_content['message']}")

            else:
                print(
                    "----> Llego fragmento pero todavia no se encuentra ensamblado por completo")

        else:
            if (new_router.check_ttl(parsed_packet)):
                hop_address = new_router.check_routes(
                    routes_filepath, dest_address)
                print(
                    f"----> Recibido paquete con direccion de destino {dest_address}")

                if hop_address is not None:
                    hop_address, mtu = hop_address
                    fragments_list = new_router.fragment_IP_packet(buffer, mtu)
                    print(f"----> El MTU de la ruta es: {mtu}")

                    # Enviamos los fragmentos
                    for fragment in fragments_list:
                        print(
                            f"----> Redirigiendo fragmento ({fragment.decode()}) con destino final {dest_address} desde {router_address} hacia {hop_address}")
                        socket_router.sendto(fragment, hop_address)
                else:
                    print(
                        f"----> No hay rutas hacia {dest_address} para paquete {buffer.decode()}")
            else:
                print(
                    f"----> Se recibio paquete {buffer.decode()} con TTL 0, descartando")

        print("<------------------------------------>")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("----> Finalizando ejecucion")
