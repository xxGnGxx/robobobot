# AI sample stack

Sample AI solution that controls the robot based on camera feedback. A laptop is used for all logic: Raspi just listens for track speed input from the laptop over TCP.

## Instructions for running

You need to have the camera, the laptop and the robot's Raspberry Pi on the same local network, with the camera streaming video to the udp address.
You'll need this repo on both the Raspi and the laptop. Arduino's code can be found here https://github.com/semihiseri/invaderBot/tree/master/software. 


On the **laptop**, install numpy and opencv including aruco with pip (check [this link](https://stackoverflow.com/questions/45972357/python-opencv-aruco-no-module-named-cv2-aruco) for details):
```
python3 -m pip install numpy
python3 -m pip install opencv-contrib-python
```
test

Steps to run:
On the laptop,
1. Set the IP address in `laptop/aruco_coordinator_newtek.py` is the camera IP address
2. Set the IP address in `laptop/waypoint_runner.py` is the robot Raspi IP address
3. Set the `ARUCO_ID` in `laptop/waypoint_runner.py` to the robot ARUCO marker number
3. cd into folder `laptop` and run `python3 waypoint_runner.py`
4. Take an ssh connection into the Raspi, cd into folder `raspi` and run `python3 run.py` (on another terminal window)

### Debugging

If you want to run the stack without the robot, you can use the `laptop/dummy_server.py` instead. Remember to change the host IP in `waypoint_runner.py` to `127.0.0.1`!

#### Problems

Sometimes, the Raspi-to-Arduino comms link gets flooded, it will hang on both ends and stop everything.

It can be fixed by opening and closing the serial. Here is an example of a keyboard controller that opens and closes the serial: https://github.com/semihiseri/invaderBot/blob/master/software/keyboardCtl/run.py


