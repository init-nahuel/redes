import router


def main():

    new_router = router.Router()

    packet = "127.0.0.1,8885,10,347,0,00000005,0,hola!"
    print(f"----> Paquete a framentar: {packet}")
    fragments_list = new_router.fragment_IP_packet(packet.encode(), 38)

    print("----> Lista de framentos: ")
    for f in fragments_list:
        print("\n" + f.decode())
    print("--------------------------------")

    fragment = fragments_list[0]
    fragment_fragments_list = new_router.fragment_IP_packet(fragment, 36)
    print(f"----> Fragmentando primer fragmento: {fragment.decode()}")
    print("----> Se crearon los siguientes fragmentos:")
    fragments_list.remove(fragment)

    for f in fragment_fragments_list:
        print("\n" + f.decode())
    print("--------------------------------")
    print("----> Reensamblando")

    fragments_list += fragment_fragments_list
    ensambled_fragments = new_router.reassemble_IP_packet(fragments_list)
    print(f"----> Paquete reensamblado: {ensambled_fragments}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("----> Finalizando ejecucion")
