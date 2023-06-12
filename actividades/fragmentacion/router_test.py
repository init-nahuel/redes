import router


def main():
    new_router = router.Router()
    IP_packet_v1 = "127.0.0.1,8881,4,47,0,16,1,hola".encode()
    parsed_IP_packet = new_router.parse_packet(IP_packet_v1)
    IP_packet_v2_str = new_router.create_packet(parsed_IP_packet)
    IP_packet_v2 = IP_packet_v2_str.encode()
    print("IP_packet_v1 == IP_packet_v2 ? {}".format(
        IP_packet_v1 == IP_packet_v2))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n----> Finalizando ejecucion")
