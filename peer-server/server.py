import socket
import sys
import cv2
import pickle
import numpy as np
import struct

HOST = ''
PORT = 8089

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn, addr = s.accept()

### new
data = b''
payload_size = struct.calcsize("L")
while True:

    while len(str(data)) < payload_size:
        data += conn.recv(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]

    msg_size = struct.unpack("L", packed_msg_size)[0]
    while len(str(data)) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]
    ###

    frame = pickle.loads(frame_data)
    print(frame)
    cv2.imshow('frame', frame)
