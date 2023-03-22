end_of_message = "|"
buff_size_server = 4
buff_size_client = 4

def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)

def remove_end_of_message(message, end_sequence): 
    index = message.rfind(end_sequence)
    return message[:index]

def receive_full_message(socket, buff_size, end_sequence):
    recv_message, address = socket.recvfrom(buff_size)
    full_message = recv_message

    while not contains_end_of_message(full_message.decode(), end_sequence):
        recv_message, address = socket.recvfrom(buff_size)
        full_message += recv_message
    
    full_message = remove_end_of_message(full_message.decode(), end_sequence)
    full_message = full_message.encode()

    return full_message, address

def send_full_message(receiver_socket, message, end_of_message, address, receiver_buff_size):
    byte_inicial = 0

    message_sent_so_far = ''.encode()

    while True:
        max_byte = min(len(message), byte_inicial + receiver_buff_size)

        message_slice = message[byte_inicial: max_byte]

        receiver_socket.sendto(message_slice, address)

        message_sent_so_far += message_slice

        if contains_end_of_message(message_sent_so_far, end_of_message.encode()):
            break

        byte_inicial += receiver_buff_size