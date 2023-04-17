import socket
from utils import *
from dnslib import DNSRecord

new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 8000)
new_socket.bind(address)

while True:
    query_msg, address_query = new_socket.recvfrom(4096)
    print("<<----------------------------->>")
    print(DNSRecord.parse(query_msg))
    print("<<----------------------------->>")
    
    resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    response = resolver(query_msg, resolver_socket)
    if response == '':
        pass # Ke hago?
    
    new_socket.sendto(response, address_query)