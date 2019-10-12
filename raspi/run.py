#!/usr/bin/env python3

import socket
import serial
from serial import Serial
import time

ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
ser.isOpen()

PORT = 1222        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('', PORT))
    print("Binded to port %i"%(PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(20)
            if not data:
                break

            # print data
            ser.write(data)
            print("Received", data, "at", time.time())
            time.sleep(0.005)

ser.write(b"L0 R0 G")
