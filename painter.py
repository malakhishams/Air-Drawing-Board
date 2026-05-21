import mediapipe as mp
import numpy as np
import cv2
import time
import os
import HandTrackerModel as model

'''
1- import image [DONE]
2- find hand landmarks [DONE]
3- check which fingers are up [DONE]
4- selection mode = 3 fingers are up
5- drawing mode = index finger is up
'''
header = cv2.imread('assets/pens-use.jpg')
header = cv2.resize(header, (1280, 75))

actual_width, actual_height = 730, 1200
#actual_width, actual_height = 640, 480

header = cv2.resize(header, (actual_width, 75))

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame.")
    exit()

# Resize frame to 640x480
frame = cv2.resize(frame, (730, 1200))
actual_height, actual_width = frame.shape[:2]
frame = cv2.flip(frame, 1)
header = cv2.resize(header, (actual_width, 75))
cap.set(3, 730)
cap.set(4, 1200)
print(actual_width, actual_height)
detector = model.HandDetector(detectconf = 0.8)
DrawColor = (0,0,0)
color_regions = [
    (40, 160, (227, 172, 9)),      # Blue
    (296, 400, (230, 190, 250)),   # Lavender 
    (560, 680, (91, 179, 116)),    # Green
    (832, 960, (0, 0, 255)),       # Red
    (1080, 1280, (0, 0, 0))        # Black
]
PenThikness = 8
EraserThikness = 53
xp, yp = 0, 0
canvas = np.zeros((actual_height, actual_width, 3), np.uint8)

clear = False

while True:
        #while cap.isOpened():
            ret, frame = cap.read()
            #if ret:
               # actual_height, actual_width = frame.shape[:2]
            frame = cv2.flip(frame, 1)
            frame = detector.FindHands(frame)
            landmarklist = detector.FindPosition(frame, draw = False)
            if len(landmarklist) != 0 :
                #print(landmarklist)
                x1, y1 = landmarklist[8][1:]
                x2, y2 = landmarklist[4][1:]
            
                fingers = detector.FingerUp()
                #print(fingers)

                if fingers[0] and fingers[1] and not fingers[3]:    #SELECTION
                    xp, yp = 0, 0

                    if y1 <= 75:
                        #CHOOSE COLOR
                        if 40 < x1 < 100:
                            DrawColor = (227, 172, 9)
                            status_text = ('Color: Blue', DrawColor, 1.5)
                        elif 130 < x1 < 244:
                            DrawColor = (179, 79, 142)
                            status_text = ('Color: Lavender', DrawColor, 1.2)
                        elif 295 < x1 < 350:
                            DrawColor = (116, 179, 91)
                            status_text = ('Color: Green', DrawColor, 1.5)
                        elif 395 < x1 < 509:
                            DrawColor = (15,15,217)
                            status_text = ('Color: Red', DrawColor, 1.5)
                        elif 570 < x1 <640:
                            DrawColor = (0, 0, 0)
                            status_text = ('ERASER', DrawColor, 2)
                    
                if fingers[1] and fingers[0] == False:  #DRAWING
                    cv2.circle(frame, (x1, y1), 7, DrawColor, cv2.FILLED)
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1 

                    if DrawColor == (0, 0, 0):
                        cv2.line(frame, (xp, yp), (x1, y1), DrawColor, EraserThikness)
                        cv2.line(canvas, (xp, yp), (x1, y1), DrawColor, EraserThikness)
                    else:
                        cv2.line(frame, (xp, yp), (x1, y1), DrawColor, PenThikness)
                        cv2.line(canvas, (xp, yp), (x1, y1), DrawColor, PenThikness)

                    xp, yp = x1, y1

                
                if all(fingers) :
                    canvas = np.zeros((actual_height, actual_width, 3), np.uint8)
                    status_text = ('Canvas Cleared!', (0, 0, 0), 1)
                    xp, yp = 0, 0

            grayframe = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, invframe = cv2.threshold(grayframe, 50, 255, cv2.THRESH_BINARY_INV)
            invframe = cv2.cvtColor(invframe, cv2.COLOR_GRAY2BGR)
            # Ensure invframe matches frame size
            if invframe.shape != frame.shape:
                invframe = cv2.resize(invframe, (frame.shape[1], frame.shape[0]))
            frame = cv2.bitwise_and(frame, invframe)
            # Ensure canvas matches frame size
            if canvas.shape != frame.shape:
                canvas = cv2.resize(canvas, (frame.shape[1], frame.shape[0]))
            frame = cv2.bitwise_or(frame, canvas)


            # Resize header to match frame width before overlay
            header_resized = cv2.resize(header, (frame.shape[1], 75))
            frame[0:75, 0:frame.shape[1]] = header_resized
            # Draw status text after header overlay so it is visible
            if 'status_text' in locals():
                text, color, scale = status_text
                cv2.putText(frame, text, (int(frame.shape[1]/2), int(frame.shape[0]/2)),
                            cv2.FONT_HERSHEY_COMPLEX, scale, color, 2, cv2.LINE_AA)
                del status_text
            cv2.imshow('frame', frame)
            cv2.imshow('canvas', canvas)
            
            if cv2.waitKey(1) == ord('q'):
                break
cap.release()
cv2.destroyAllWindows()
