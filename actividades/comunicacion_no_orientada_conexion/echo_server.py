import socket
from utils import *

# Create the UDP socket
print("Creating server socket")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = ("localhost", 5000)

# Bind the socket to address
server_socket.bind(address)

# Receive message
# message, message_address = server_socket.recvfrom(10)

while True:
    message, message_address = receive_full_message(server_socket, buff_size_server, end_of_message)

    # Print the message
    print(f"Received message: '{message.decode()}'")

    # Echo reply
    print(f"Sending message '{message.decode()}' to {message_address}")
    # server_socket.sendto(message, message_address)
    send_full_message(server_socket, message, end_of_message, message_address, buff_size_client)