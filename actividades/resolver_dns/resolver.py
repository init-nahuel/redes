import socket
from utils import *

resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 8000)
resolver_socket.bind(address)

while True:
    query_msg, address_query = resolver_socket.recvfrom(4096)
    
    print(query_msg)

    parse_dns_msg(query_msg)