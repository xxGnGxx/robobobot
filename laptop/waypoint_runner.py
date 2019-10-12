import math
import time
import socket
import cv2
import numpy as np

import aruco_coordinator_newtek as aruco_coordinator
# import aruco_coordinator # switch to this for Raspi camera

HOST = '192.168.43.194'#'10.42.0.65'  # The server's (robot's) hostname or IP address
HOST = '192.168.1.56'#'10.42.0.65'  # The server's (robot's) hostname or IP address
#HOST = '127.0.0.1'#'10.42.0.65'  # The server's (robot's) hostname or IP address
PORT = 1222        # The port used by the server
ARUCO_ID = 10 # Your robot's ARUCO ID
ARUCO_ID = 15 # Your robot's ARUCO ID
fast = cv2.FastFeatureDetector_create()

# Set the range of HSV for ball detection here
# You may need to recalibrate when lighting conditions change
PINK_HSV_RANGE = (
    np.array([200, 180, 200]),
    np.array([230, 255, 255])
)

YELLOW_HSV_RANGE = (
    np.array([20,130,100]),
    np.array([64, 255, 255])
)


class Botsy:
    
    # Initalize the motors.
    def __init__(self, socket):
        self.lastPos = (0, 0, 0)
        self.socket = socket
        self.socket.connect((HOST, PORT))

    # Send text followed by a newline character
    def sendl(self, text = ""):
        self.socket.send(text.encode())

    # Receives maxlength characters and strips whitespace
    def receive(self, maxlength):
        request = self.socket.recv(maxlength + 1) # +1 for the trailing newline character
        return request.strip() # drop all trailing and prepending whitespace

    # Set the velocity of left and right motors [-1, 1].
    def set_motors(self, left, right):
        self.sendl("L%i R%i "%(left, right))
    
    def detect_balls(self, fast, img):
        """Detect balls in image, return coordinates as list."""

        kps = fast.detect(img,None)
        kps = bot.merge_keypoints(kps, 20)

        return [kp.pt for kp in kps]

    def distance_between_points(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def has_close_points(self, point, others, radius):
        for other in others:
            if (bot.distance_between_points(point.pt, other.pt) < radius):
                return True
        return False

    def merge_keypoints(self, keypoints, radius):
        result = []
        for point in keypoints:
            if (not bot.has_close_points(point, result, radius)):
                result += [point]

        return result


    # Returns the position of the robot in [x, z, angle] format
    # The coordinate system is as follows (top-down view)
    #  .-------------------->x
    #  |\  (angle)
    #  | \
    #  |  \
    #  |   \
    #  |    \
    #  |     \
    #  |
    #  V
    #  z
    #
    def get_position(self):
        corners, ids, frame = aruco_coordinator.get_markers()
        if len(corners) > 0:
            for i in range(len(corners)):
                #print(ids[i])
                if ids[i] == ARUCO_ID:
                    c = corners[i][0]   
                    x = 0.25 * (c[0][0] + c[1][0] + c[2][0] + c[3][0])
                    z = 0.25 * (c[0][1] + c[1][1] + c[2][1] + c[3][1])
                    theta = math.atan2(c[0][1] - c[1][1], c[0][0] - c[1][0])
                    pos = (x, z, theta)
                    self.lastPos = pos
                    break
        return self.lastPos
    
    def startGetBalls(self):
        while(True):
            ret, frame = aruco_coordinator.getFrame()
            frame = cv2.bitwise_and(frame, frame, mask= bot.get_yellow_balls(frame))
            #cv2.imshow("mask", frame)
            balls = bot.detect_balls(fast, frame)
            print(balls)
            if cv2.waitKey(1) == 23:
                break
            return balls


    def get_balls(self, frame, color_hsv_range):
        if frame is None:
            print("No frame given")
            return []

        # Blur the frame to remove high frequency noise
        frame = cv2.GaussianBlur(frame, (5, 5), 0)

        # Convert the colorspace to HSV (Hue, Saturation, Value)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # We want to look for bright, multicolored balls. That means we want to extract parts of the image with:
        # Specified hue
        # High saturation
        # High value
        mask = cv2.inRange(hsv, color_hsv_range[0], color_hsv_range[1])
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        return mask

    # Returns the position of the green balls
    def get_pink_balls(self, frame):
        return self.get_balls(frame, PINK_HSV_RANGE)

    # Returns the position of the green balls
    def get_yellow_balls(self, frame):
        return self.get_balls(frame, YELLOW_HSV_RANGE)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    bot = Botsy(s)
    # Set to True if playing as RED
    FLIP_COORDINATES = False

    # TODO these are in pixel coordinates: needs to be calibrated into
    # arena coordinates
    patrolTargets = [
        [800, 800],
        [800, 200],
        [200, 200]
    ]

    target_id = 0
    speed = 100 # robot speed
    lastX = 0
    lastY = 0
    lastPosCount = 0 # shit

    # main loop
    while True:
        # For AI solutions, this is a good starting point: it is enough
        # to keep the current target updated
        target = patrolTargets[target_id] # get the target from list

        pos = bot.get_position()
        arr = bot.startGetBalls()
        
        if(FLIP_COORDINATES):
            pos = (-pos[0], -pos[1], pos[2] + math.pi)

        dx = target[0] - pos[0] # difference in x
        dz = target[1] - pos[1] # difference in z

        da = math.atan2(dz, dx) # difference in angle
        da += math.pi/2

        ra = pos[2] - da # relative angle between robot orientation and the goal
        if ra > math.pi:
            ra -= 2 * math.pi
        if ra < -math.pi:
            ra += 2 * math.pi

        ra *= 57
            
        #print("targeting", target, "rel angle", ra)
        print(lastX-pos[0])
        print(lastY-pos[1])
        #if(lastPosCount == 10):
            #Reverse
        if(abs(lastX-pos[0]) < 2. and abs(lastY-pos[1]) < 2.):
            lastPosCount += 1
        print(lastPosCount)
        lastX = pos[0]
        lastY = pos[1]

        #turn the face towards the goal; about 10 degrees of precision is sufficient. Then march!
        limit = 40.
        limitn = -40.

        if ra < limitn or ra > limit:
            bot.set_motors(speed, 0) # turn right
            bot.set_motors(0, 0) # turn right
       ## elif ra > limit:
          ##  bot.set_motors(0, speed) # turn left
        else:
            bot.set_motors(speed, speed) # go straight
        #print(abs(dx) + abs(dz))
        if (abs(dx) + abs(dz) <= 40): # switch to the next target if close enough
            target_id += 1
            target_id %= len(patrolTargets)

aruco_coordinator.release()

