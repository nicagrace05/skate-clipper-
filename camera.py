import cv2

cap = cv2.VideoCapture(0) #zero is first available camera device 
if not cap.isOpened() : 
    raise RuntimeError('couldnt open camera')

while True :
    ret, frame = cap.read()
    if not ret : 
        break
    cv2.imshow('camera')
    