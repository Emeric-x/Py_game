import cv2

class mpHands:
    import mediapipe as mp
    def __init__(self, maxHands=2, model_complexity=1, tol1=.5, tol2=.5):
        self.hands = self.mp.solutions.hands.Hands(False, maxHands, model_complexity, tol1, tol2)
    def Marks(self, frame):
        myHands = []
        handsType = []
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)
        if results.multi_hand_landmarks != None:
            for hand in results.multi_handedness:
                handType = hand.classification[0].label
                handsType.append(handType)
            for handLandMarks in results.multi_hand_landmarks:
                myHand = []
                for landMark in handLandMarks.landmark:
                    myHand.append((int(landMark.x*width), int(landMark.y*height)))
                myHands.append(myHand)
        return myHands, handsType

width=1280
height=720

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cam.set(cv2.CAP_PROP_FPS, 60)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

findHands = mpHands()

paddleWidth = 25
paddleHeight = 125
paddleColor = (255,0,255)
ballRadius = 25
ballColor = (255,0,0)
xPos = int(width/2)
yPos = int(height/2)
deltaX = 25
deltaY = 25
font = cv2.FONT_HERSHEY_SIMPLEX
fontHeight = 5
fontWeigth = 5
fontColor = (0,0,255)
yLeftTip = 0
yRightTip = 0
scoreLeft = 0
scoreRight = 0

while True:
    ignore, frame = cam.read()
    frame = cv2.resize(frame, (width, height))
    cv2.circle(frame, (xPos, yPos), ballRadius, ballColor, -1)
    cv2.putText(frame, str(scoreLeft), (50, 125), font, fontHeight, fontColor, fontWeigth)
    cv2.putText(frame, str(scoreRight), (width-150, 125), font, fontHeight, fontColor, fontWeigth)
    handData, handsType = findHands.Marks(frame)
    for hand, handType in zip(handData, handsType):
        # if handType=='Right':
        #     handColor = (255,0,0)
        # if handType=='Left':
        #     handColor = (0,0,255)
        # for index in [0,5,6,7,8]:
        #    cv2.circle(frame, hand[index], 15, handColor, 5)
        if handType=='Left':
            # ici [1] correspond a yposition (verticalement)
            yLeftTip = hand[8][1]
        if handType=='Right':
            yRightTip = hand[8][1]

    cv2.rectangle(frame, (0, int(yLeftTip-paddleHeight/2)), (paddleWidth, int(yLeftTip+paddleHeight/2)), paddleColor, -1)
    cv2.rectangle(frame, (width-paddleWidth, int(yRightTip-paddleHeight/2)), (width, int(yRightTip+paddleHeight/2)), paddleColor, -1)
    topBallEdge = yPos-ballRadius
    bottomBallEdge = yPos+ballRadius
    leftBallEdge = xPos-ballRadius
    rightBallEdge = xPos + ballRadius

    if topBallEdge<=0:
        deltaY = deltaY*(-1)
    if bottomBallEdge>=height:
        deltaY = deltaY*(-1)
    if leftBallEdge<=paddleWidth:
        if yPos>=int(yLeftTip-paddleHeight/2) and yPos<=int(yLeftTip+paddleHeight/2):
            deltaX = deltaX*(-1)
        else:
            xPos = int(width/2)
            yPos = int(height/2)
            scoreRight += 1
    if rightBallEdge>=width-paddleWidth:
        if yPos>=int(yRightTip-paddleHeight/2) and yPos<=int(yRightTip+paddleHeight/2):
            deltaX = deltaX*(-1)
        else:
            xPos = int(width/2)
            yPos = int(height/2)
            scoreLeft += 1

    xPos = xPos+deltaX
    yPos = yPos+deltaY

    if scoreLeft+scoreRight>=10:
        break

    cv2.imshow('myWC', frame)
    cv2.moveWindow('myWC', 0, 0)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cam.release()