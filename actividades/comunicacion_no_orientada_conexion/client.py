import socket
from utils import *

# Create the UDP socket
print("Creating client socket")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ("localhost", 5000)
file = open("dummy.txt", 'r')
message = file.read()

message += end_of_message

# Send the message to address
print(f"Sending message '{message}' to {address}")
# client_socket.sendto(message.encode(), address)
send_full_message(client_socket, message.encode(), end_of_message, address, buff_size_server)

# Receive the echo message from address
# recv_message, address = client_socket.recvfrom(1024)
recv_message, address = receive_full_message(client_socket, buff_size_client, end_of_message)

print(f"Received message: '{recv_message.decode()}'")

if recv_message.decode() != message:
    print("\n WARNING: LOSS PACKETS")
else:
    print("\n FULL MESSAGE SENDED :D")