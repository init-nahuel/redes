import socket
import sys
import router


def main():
    _, router_ip, router_port, routes_filepath = sys.argv

    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    router_address = (router_ip, int(router_port))

    socket_router.bind(router_address)

    new_router = router.Router(socket_router, router_address)

    print(f"----> La IP del router es: {router_ip}")
    print(f"----> El puerto del router es: {router_port}")
    print(f"----> Mostrando archivo con rutas:")
    with open(routes_filepath, "r") as f:
        print(f.read())
    print("<------------------------------------>")

    while True:
        buffer, _ = socket_router.recvfrom(1026)
        possible_msg = new_router.parse_packet(buffer)
        dest_address = (possible_msg['dest_ip'],
                        int(possible_msg['dest_port']))

        if (dest_address == router_address):
            print(
                f"----> Llego mensaje a este router ({router_address}), mostrando contenido: {possible_msg['message']}")
        else:
            hop_address = new_router.check_routes(
                routes_filepath, dest_address)
            print(
                f"----> Recibido paquete con direccion de destino {dest_address}")
            if hop_address != None:
                print(
                    f"----> Redirigiendo paquete {buffer.decode()} con destino final {dest_address} desde {router_address} hacia {hop_address}")
                socket_router.sendto(buffer, hop_address)
            else:
                print(
                    f"----> No hay rutas hacia {dest_address} para paquete {buffer.decode()}")

        print("<------------------------------------>")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n----> Finalizando ejecucion de router")
