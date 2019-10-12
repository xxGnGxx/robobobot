#!/usr/bin/env python3

import socket
import serial
from serial import Serial
import time
import robohat

robohat.init()
speed = 100

ser = serial.Serial(port='/dev/ttyAMA0', baudrate=9600)
ser.isOpen()

PORT = 1222        # Port to listen on (non-privileged ports are > 1023)
debug = False

def log(text):
    if(debug): print(text)

def _int(s):
    s = s.strip()
    return int(s) if s else 0

def calculateAndRun(motorArray):
    lastLeft = 0
    right = 0
    left = 0

    for motorData in motorArray:
        #print("mdata  " + motorData)
        if(motorData == ''):
            continue
        if(motorData[0] == 'L'):
            left = _int(motorData.split('L')[1]) 
        elif(motorData[0] == 'R'):
            lastLeft = left # assign only if right motor is read (end of packet)
            right = _int(motorData.split('R')[1])


    if(lastLeft > 0 and right > 0):
        log("forward")
        robohat.forward(speed)
    elif(lastLeft > 0):
        log("left")
        robohat.spinLeft(speed)
        #robohat.turnForward(0, 100)
    elif(right > 0):
        log("right")
        robohat.spinRight(speed)
    else:
        robohat.stop()

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', PORT))
        print("Binded to port %i"%(PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:

            print('Connected by', addr)
            while True:
                data = conn.recv(12)
                if not data: break
            
                socketString = data.decode("UTF-8")
                motorArray = socketString.split(' ')
                calculateAndRun(motorArray)

finally:
    print("What a glourious battle!")