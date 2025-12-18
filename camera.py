import cv2

cap = cv2.VideoCapture(0) #zero is first available camera device 
if not cap.isOpened() : 
    raise RuntimeError('couldnt open camera')

while True :
    ret, frame = cap.read() #frame is HxWx3, for BGR channels, vals from 0-255
    if not ret : 
        print('failed to get frame')
        break
    cv2.imshow('Camera', frame) #creates window to display current array
    if cv2.waitKey(1) & 0xFF == ord('q') : 
        break #exits loop when press q

cap.release() #returning the hardware 
cv2.destroyAllWindows()


    