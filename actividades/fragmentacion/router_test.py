import router
import socket
import sys

def main():
    _, router_ip, router_port, routes_filepath = sys.argv

    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    router_address = (router_ip, int(router_port))

    socket_router.bind(router_address)

    new_router = router.Router()

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
            print(
                f"----> Llego el siguiente paquete a este router: {buffer.decode()}, mostrando contenido: {parsed_packet['message']}")
        else:
            if (new_router.check_ttl(parsed_packet)):
                hop_address = new_router.check_routes(routes_filepath, dest_address)
                print(f"----> Recibido paquete con direccion de destino {dest_address}")

                if hop_address[0]:
                    print(f"----> Redirigiendo paquete {buffer.decode()} con destino final {dest_address} desde {router_address} hacia {hop_address[0]}")
                    print(f"El MTU es {hop_address[1]}")
                    socket_router.sendto(buffer, hop_address[0])
                else:
                    print(f"----> No hay rutas hacia {dest_address} para paquete {buffer.decode()}")
            else:
                print(f"----> Se recibio paquete {buffer.decode()} con TTL 0, descartando")
        
        print("<------------------------------------>")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n----> Finalizando ejecucion")
