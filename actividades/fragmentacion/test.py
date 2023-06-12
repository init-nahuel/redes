import router


def main():

    new_router = router.Router()

    packet = "127.0.0.1,8885,10,347,0,00000005,0,hola!"
    fragments_list = new_router.fragment_IP_packet(packet.encode(), 38)

    print(fragments_list)

    for p in fragments_list:
        print(p.decode())
        print("-----------------")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("----> Finalizando ejecucion")
