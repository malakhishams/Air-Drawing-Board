import mediapipe as mp
import cv2
import time
 

class HandDetector():
    def __init__(self, mode = False, MaxHands = 2, model_complexity=1, detectconf = 0.5, trackconf = 0.5 ):
        self.mode = mode
        self.maxhands = MaxHands
        self.detectconf = detectconf
        self.trackconf = trackconf
        self.mphands = mp.solutions.hands
        self.hands = self.mphands.Hands(self.mode, self.maxhands, 1, self.detectconf, self.trackconf)
        self.mpdraw = mp.solutions.drawing_utils
        self.tipsID = [4, 8, 12, 16, 20]


    def FindHands(self, frame, draw = True):
        #frame = cv2.flip(frame, 1)
        RGBimg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(RGBimg)
        if self.result.multi_hand_landmarks:
            for handlandmark in self.result.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(frame, handlandmark, self.mphands.HAND_CONNECTIONS)
        return frame
    
    def FindPosition(self, frame, handnum = 0, draw = True):
        self.landmarkslist = []
        if self.result.multi_hand_landmarks:
            thehand = self.result.multi_hand_landmarks[handnum]
            for id, lm in enumerate(thehand.landmark):
                        h, w, c = frame.shape
                        px, py = int(lm.x * w), int(lm.y * h)
                        self.landmarkslist.append([id, px, py])
        return self.landmarkslist
    
    def FingerUp(self):
        fingers = []
        if self.landmarkslist[self.tipsID[0]][1] < self.landmarkslist[self.tipsID[0]-1][1]:
             fingers.append(1)
        else:
             fingers.append(0)
        for id in range(1, 5):
             if self.landmarkslist[self.tipsID[id]][2] < self.landmarkslist[self.tipsID[id]-2][2]:
                  fingers.append(1)
             else:
                 fingers.append(0)
        return fingers



def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    while True:
        ret, frame = cap.read()
        frame = detector.FindHands(frame)
        landmarkslist = detector.FindPosition(frame)
        if len(landmarkslist) != 0:
            print(landmarkslist[8])
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()