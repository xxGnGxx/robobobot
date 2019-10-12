import numpy as np
import cv2
from cv2 import aruco

# over wifi (phone hotspot)
#url = "http://192.168.43.48:8000/stream.mjpg"
# over ethernet (local switch)
url = "http://10.42.0.240:8000/stream.mjpg"
url = "ArucoVideo.ts"

cap = cv2.VideoCapture(url)

# get vcap property, float(v,h)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

parameters =  aruco.DetectorParameters_create()
# Use Aruco Dictionary for 4x4 markers (250)
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)

def get_markers():
   # Capture frame-by-frame
   ret, frame = cap.read()
   
   if ret:
       corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

       return corners, ids
   return ([], [])

def release():
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
