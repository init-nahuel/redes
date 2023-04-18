import socket
from utils import *
from dnslib import DNSRecord

new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creamos el socket para obtener mensajes DNS

address = ('localhost', 8000)
new_socket.bind(address) # Nos mantenemos a la espera de recepcion de mensajes

while True:
    query_msg, address_query = new_socket.recvfrom(4096) # Recibimos la query
    print("<<----------------------------->>")
    print(f"[NEW QUERY] (debug) Recibiendo query desde IP: {address_query}")
    print("<<----------------------------->>")
    resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creamos el socket del resolver
    response = resolver(query_msg, resolver_socket)  # Procesamos la query con el resolver
    print("<<----------------------------->>")
    ip = parse_dns_msg(response)['answer']['resource_records_list'][0].rdata
    print(f"(debug) Respuesta recibida IP por resolver: {ip}, enviando a direccion: {address_query}")
    print("<<----------------------------->>")
    new_socket.sendto(response, address_query) # Enviamos la respuesta del resolver a la direccion de donde llego la query