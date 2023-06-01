import socket
import sys
import router


_, router_ip, router_port, routes_filepath = sys.argv

socket_router_1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

router_1_address = (router_ip, int(router_port))

socket_router_1.bind(router_1_address)

router_1 = router.Router(socket_router_1, router_1_address, "caca")

print(f"----> La IP del router es: {router_ip}")
print(f"----> El puerto del router es: {router_port}")
print(f"----> Mostrando archivo con rutas:")
with open(routes_filepath, "r") as f:
    print(f.read())

# while True:
    # buffer, _ = socket_router_1.recvfrom(1026)
    # print(f"----> Monstrando mensaje obtenido: {buffer.decode()}")

IP_packet_v1 = "127.0.0.1,8881,hola".encode()
parsed_IP_packet = router_1.parse_packet(IP_packet_v1)
IP_packet_v2_str = router_1.create_packet(parsed_IP_packet)
IP_packet_v2 = IP_packet_v2_str.encode()
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))