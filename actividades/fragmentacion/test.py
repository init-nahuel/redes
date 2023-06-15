import router


def main():

    new_router = router.Router()

    packet = "127.0.0.1,8885,10,347,0,00000005,0,hola!"
    fragments_list = new_router.fragment_IP_packet(packet.encode(), 38)

    print(f"----> Paquete a framentar: {packet}")

    print("----> Lista de framentos: ")
    for f in fragments_list:
        print(f.decode() + "\n")
    print("--------------------------------")
    
    ensambled_fragments = new_router.reassemble_IP_packet(fragments_list)
    print(f"----> Paquete reensamblado: {ensambled_fragments}")

    # fragment_fragment_list = new_router.fragment_IP_packet(fragments_list[1], 36)
    # print(fragment_fragment_list)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("----> Finalizando ejecucion")
