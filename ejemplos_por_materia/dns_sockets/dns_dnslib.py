import socket
from dnslib import DNSRecord

def send_dns_message(address, port):
    # Aca ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
    qname = "example.com"
    q = DNSRecord.question(qname)
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Lo enviamos, hacemos cast a bytes de lo que resulte de la funcion pack() sobre el mensaje
        sock.sendto(bytes(q.pack()), server_address)
        # En data quedara la respuesta a nuestra consulta
        data, _ = sock.recvfrom(4096)
        # Le pedimos a dnslib que haga el trabjao de parsing por nosotros
        d = DNSRecord.parse(data)
    finally:
        sock.close()
    # OBS: Los datos de la respuesta van en una estructura de datos
    return d

# Es dnslib la que sabe como se debe imprimir la estructura, usa el mismo formato que dig, los datos
# NO vienen en un string gigante, sino en una estructura de datos
print(send_dns_message('8.8.8.8', 53))