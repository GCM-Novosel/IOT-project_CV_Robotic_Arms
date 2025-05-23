import cv2
import mediapipe as mp
from math import hypot
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0)

# Initialize MediaPipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()  # Capture image
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB

    results = hands.process(imgRGB)  # Process hand gestures

    lmList = []
    if results.multi_hand_landmarks:  # If hands are detected
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

    if lmList:
        # Extract landmark coordinates
        xs, ys = lmList[9][1], lmList[9][2]  # Side reference point for thumb
        x0, y0 = lmList[0][1], lmList[0][2]  # Bottom reference point
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb
        x2, y2 = lmList[8][1], lmList[8][2]  # Index finger
        x3, y3 = lmList[12][1], lmList[12][2]  # Middle finger
        x4, y4 = lmList[16][1], lmList[16][2]  # Ring finger
        x5, y5 = lmList[20][1], lmList[20][2]  # Pinkie
        x6, y6 = lmList[9][1], lmList[9][2]  # Relation reference

        # Draw circles at finger tips
        cv2.circle(img, (x1, y1), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x3, y3), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x4, y4), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x5, y5), 13, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x6, y6), 13, (0, 255, 0), cv2.FILLED)

        # Draw lines for measurement
        cv2.line(img, (x1, y1), (xs, ys), (255, 0, 0), 3)
        cv2.line(img, (x0, y0), (x6, y6), (255, 0, 0), 3)
        cv2.line(img, (x2, y2), (x0, y0), (255, 0, 0), 3)
        cv2.line(img, (x3, y3), (x0, y0), (255, 0, 0), 3)
        cv2.line(img, (x4, y4), (x0, y0), (255, 0, 0), 3)
        cv2.line(img, (x5, y5), (x0, y0), (255, 0, 0), 3)

        # Calculate distances
        length_sc = hypot(x0 - x6, y0 - y6)
        length_thumb = hypot(xs - x1, ys - y1)
        length_index = hypot(x0 - x2, y0 - y2)
        length_middle = hypot(x0 - x3, y0 - y3)
        length_ring = hypot(x0 - x4, y0 - y4)
        length_pinkie = hypot(x0 - x5, y0 - y5)

        # Normalize distances
        thumb = np.around((length_thumb / length_sc), 2)
        index = np.around((length_index / length_sc), 2)
        middle = np.around((length_middle / length_sc), 2)
        ring = np.around((length_ring / length_sc), 2)
        pinkie = np.around((length_pinkie / length_sc), 2)

        # Map to servo angles (0-180 degrees)
        thumb = np.interp(thumb, [0.4, 1.0], [180, 0])
        index = np.interp(index, [0.9, 1.7], [180, 0])
        middle = np.interp(middle, [0.8, 1.9], [180, 0])
        ring = np.interp(ring, [0.8, 1.8], [180, 0])
        pinkie = np.interp(pinkie, [0.6, 1.6], [180, 0])
        angles = [int(pinkie), int(ring), int(middle), int(index), int(thumb)]
        print(angles)


    cv2.imshow('Image', img)  # Display video
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()  # Release camera
cv2.destroyAllWindows()  # Close windows