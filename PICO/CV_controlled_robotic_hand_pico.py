import cv2
import mediapipe as mp
from math import hypot
import numpy as np
import serial

# Open Pico serial port (update COM port as needed)
try:
    pico = serial.Serial('COM5', 115200, timeout=1)
except Exception as e:
    print("Failed to open Pico serial:", e)
    exit()

cap = cv2.VideoCapture(0)  # initialize camera

mpHands = mp.solutions.hands  # mediapipe hand detect library
hands = mpHands.Hands()  # complete the initialization configuration of hands
mpDraw = mp.solutions.drawing_utils


while True:
    success, img = cap.read()  # If camera works capture image
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to rgb because cv2 has genius ideas

    results = hands.process(imgRGB)  # Collection of gesture information

    lmList = []
    if results.multi_hand_landmarks:  # list of all hands detected.
        # By accessing the list, we can get the information of each hand's corresponding flag bit
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):  # adding counter and returning it
                # Get finger joint points
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])  # adding to the empty list 'lmList'
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

    if lmList != []:

        xs, ys = lmList[9][1], lmList[9][2] # side reference point for thumb
        x0, y0 = lmList[0][1], lmList[0][2] # bottom reference point
        x1, y1 = lmList[4][1], lmList[4][2]  # thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # index finger
        x3, y3 = lmList[12][1], lmList[12][2]  # middle finger
        x4, y4 = lmList[16][1], lmList[16][2]   # ring finger
        x5, y5 = lmList[20][1], lmList[20][2]   # pinkie
        x6, y6 = lmList[9][1], lmList[9][2]     #relation reference

        # creating circles at the tips of fingers
        cv2.circle(img, (x1, y1), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x3, y3), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x4, y4), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x5, y5), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x6, y6), 13, (0, 255, 0), cv2.FILLED)


        cv2.line(img, (x1, y1), (xs, ys), (255, 0, 0), 3) # drawing lines that we measure for controll
        cv2.line(img, (x0, y0), (x6, y6), (255, 0, 0), 3)
        cv2.line(img, (x2, y2), (x0, y0), (255, 0, 0), 3)
        cv2.line(img, (x3, y3), (x0, y0), (255, 0, 0), 3)
        cv2.line(img, (x4, y4), (x0, y0), (255, 0, 0), 3)
        cv2.line(img, (x5, y5), (x0, y0), (255, 0, 0), 3)

        length_sc = hypot(x0 - x6, y0 - y6)     #calcutalting distances between points
        length_thumb = hypot(xs - x1, ys - y1)
        length_index = hypot(x0 - x2, y0 - y2)
        length_middle = hypot(x0 - x3, y0 - y3)
        length_ring = hypot(x0 - x4, y0 - y4)
        length_pinkie = hypot(x0 - x5, y0 - y5)

        thumb = np.around((length_thumb/length_sc),2)   #dividing values to get normalized values always, no matter of
        index = np.around((length_index/length_sc),2)       #the distance of the hand in front of the camera
        middle =np.around((length_middle/length_sc),2)
        ring = np.around((length_ring/length_sc),2)
        pinkie = np.around((length_pinkie/length_sc),2)


        thumb = np.interp(thumb, [0.4, 1.0], [120, 0])      #normalizing the range of values according to each finger's geometry
        index = np.interp(index, [0.9, 1.7], [180, 0])
        middle = np.interp(middle, [0.8, 1.9], [180, 0])
        ring = np.interp(ring, [0.7, 1.8], [180, 0])
        pinkie = np.interp(pinkie, [0.6, 1.6], [180, 0])


        #create a string in format for Arduino:

        angles = [int(middle), int(ring), int(index), int(pinkie), int(thumb)]
        msg = ",".join(map(str, angles)) + "\n"

        try:
            pico.write(msg.encode('utf-8'))
            pico.flush()
        except Exception as e:
            print("Error sending to Pico:", e)

    cv2.imshow('Image', img)  # Show the video
    if cv2.waitKey(1) & 0xff == ord(' '):
        break

cap.release()  # stop cam
cv2.destroyAllWindows()  # close window