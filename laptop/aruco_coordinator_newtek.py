import numpy as np
import cv2
from cv2 import aruco

# Needs to match the camera IP address
url = "udp://@224.0.0.0:1234"
#url = "ArucoVideo.ts"

cap = cv2.VideoCapture(url)

# get vcap property 
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("Connected to camera, resolution is %ix%i" % (width, height))

parameters =  aruco.DetectorParameters_create()
# Use Aruco Dictionary for 4x4 markers (250)
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)

def get_markers():
    ret, frame = getFrame()

    if (frame is None):
        print("frame could not be read.")

        cap.release()
        cap.open(url)

        return ([], [])

    if ret:
       corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
       return corners, ids, frame

    return ([], [])

def getFrame():
    for i in range(0,10):
        cap.grab()
    ret, frame = cap.read() # start using the frame
    return ret, frame    

def release():
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
