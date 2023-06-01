import socket
import sys

_, router_ip, router_port, routes_filepath = sys.argv

print(f"----> La IP del router es: {router_ip}")
print(f"----> El puerto del router es: {router_port}")
print(f"----> Mostrando archivo con rutas:")
with open(routes_filepath, "r") as f:
    print(f.read())