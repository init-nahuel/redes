import socketTCP

address = ('localhost', 8000)

server_socketTCP = socketTCP.SocketTCP()

print("-----------Handshake-----------")
server_socketTCP.bind(address)
connection_socketTCP, new_address = server_socketTCP.accept()
print("-----------Handshake-----------")

# test 1
print("-----------TEST 1-----------")
buff_size = 16
full_message = connection_socketTCP.recv(buff_size)
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode():
    print("Test 1: Passed")
else:
    print("Test 1: Failed")
print("-----------TEST 1-----------")

# test 2
print("-----------TEST 2-----------")
buff_size = 19
full_message = connection_socketTCP.recv(buff_size)
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode():
    print("Test 2: Passed")
else:
    print("Test 2: Failed")
print("-----------TEST 2-----------")

# test 3
print("-----------TEST 3-----------")
buff_size = 14
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
print("Test 3 received:", message_part_1 + message_part_2)
# print("Test 3 received:", message_part_1)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode():
    # if (message_part_1) == "Mensaje de largo 19".encode():
    print("Test 3: Passed")
else:
    print("Test 3: Failed")
print("-----------TEST 3-----------")

# test file
print("-----------TEST INPUT FILE-----------")
buff_size = 106
message_part_1 = connection_socketTCP.recv(buff_size).decode()
message_part_2 = connection_socketTCP.recv(buff_size).decode()
full_message = message_part_1 + message_part_2
print(full_message)
print("-----------TEST INPUT FILE-----------")

print("-----------Cierre de Conexion-----------")
connection_socketTCP.recv_close()
print("-----------Cierre de Conexion-----------")
