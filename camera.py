import cv2

#CAMERA ACSESS
cap = cv2.VideoCapture(0) #zero is first available camera device 
if not cap.isOpened() : 
    raise RuntimeError('couldnt open camera')

first_frame = None

while True :
    ret, frame = cap.read() #frame is HxWx3, for BGR channels, vals from 0-255
    if not ret : 
        print('failed to get frame')
        break
    
    if cv2.waitKey(1) & 0xFF == ord('q') : 
        break #exits loop when press q

        #MOTION TRACKING
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #motion is soley about intensity here
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0) #big blur to filter out noise
    first_frame = None #everything realtive to empty garage
    if first_frame is None:
        first_frame = gray_blur
        continue 
    frame_delta = cv2.absdiff(first_frame, gray_blur) #the differences in frames visualized in pixels (white=motion)
    _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY) #defining what is considered movement
    thresh = cv2.dialate(thresh, None, iterations = 2)
    contours, _, = cv2.findContours(
        thresh.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    ) #contours closed loop aaroun white areas 
    (x,y,w,h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255), 2)

    v2.imshow('Camera', frame) #creates window to display current array
    v2.imshow('Motion Mask', thresh) #shows framing window 

cap.release() #returning the hardware 
cv2.destroyAllWindows()
