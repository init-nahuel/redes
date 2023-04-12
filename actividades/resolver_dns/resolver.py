import socket
from utils import *
from dnslib import DNSRecord

resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ('localhost', 8000)
resolver_socket.bind(address)

while True:
    query_msg, address_query = resolver_socket.recvfrom(4096)
    print("<<----------------------------->>")
    print(DNSRecord.parse(query_msg))
    print("<<----------------------------->>")
    print(parse_dns_msg(query_msg))
    print("<<----------------------------->>")
    resolver(query_msg)
