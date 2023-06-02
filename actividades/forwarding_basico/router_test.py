import socket
import sys
import router


_, router_ip, router_port, routes_filepath = sys.argv

socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

router_address = (router_ip, int(router_port))

socket_router.bind(router_address)

router = router.Router(socket_router, router_address, "caca")

print(f"----> La IP del router es: {router_ip}")
print(f"----> El puerto del router es: {router_port}")
print(f"----> Mostrando archivo con rutas:")
with open(routes_filepath, "r") as f:
    print(f.read())
print("<------------------------------------>")

while True:
    buffer, _ = socket_router.recvfrom(1026)
    possible_msg = router.parse_packet(buffer)
    possible_address = (possible_msg['dest_ip'], int(possible_msg['dest_port']))
    if (possible_address == router_address):
        print(f"----> Llego mensajito: {possible_msg['message']}")
    else:
        address = router.check_routes(routes_filepath, possible_address)
        print(f"Enviando paquete a la direccion: {address}")
        socket_router.sendto(buffer, router_address)
    