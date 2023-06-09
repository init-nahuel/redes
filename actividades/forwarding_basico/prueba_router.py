import sys
import socket

def main():
    _, packets_file, dest_router_ip, dest_router_port = sys.argv 
    socket_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest_address = (dest_router_ip, int(dest_router_port))

    packets_headers_list : list
    with open(packets_file, "r") as f:
        packets_headers_list = f.read().split('\n')

    print("<------------------------------------>")
    for header in packets_headers_list:
        socket_sender.sendto(header.encode(), dest_address)
        print(f"----> Enviando header {header} a router {dest_address}")
        print("<------------------------------------>")
    
    socket_sender.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n----> Finalizando ejecucion")