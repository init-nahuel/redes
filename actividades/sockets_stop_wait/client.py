from socketTCP import SocketTCP

# program_name, ip, port = sys.argv
# file = input()

address = ('localhost', 8000)

# address = (ip, int(port))
client_socketTCP = SocketTCP()

print("----> Realizando Handshake")

client_socketTCP.connect(address)

print("----> Handshake finalizado")
