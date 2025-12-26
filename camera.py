import cv2
import math

#CAMERA ACSESS
cap = cv2.VideoCapture(0) #zero is first available camera device, camera app must be open
if not cap.isOpened() : 
    raise RuntimeError('couldnt open camera') #error with presmissions 

first_frame = None
last_centroid = None
smooth_centroid = None
delta = .7 

while True :
    ret, frame = cap.read() #frame is HxWx3, for BGR channels, vals from 0-255
    if not ret : 
        print('failed to get frame')
        break

        #MOTION TRACKING
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #motion is soley about intensity here
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0) #big blur to filter out noise
    if first_frame is None:
        first_frame = gray_blur.copy()
        continue
    alpha = .02
    first_frame = cv2.addWeighted(gray_blur, alpha, first_frame, 1-alpha, 0) #exponetial background averaging keeps only motion relavent agaisnt stationary background
    frame_delta = cv2.absdiff(first_frame, gray_blur) #the differences in frames visualized in pixels (white=motion)
    _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY) #defining what is considered movement
    thresh = cv2.dilate(thresh, None, iterations = 2)
    contors, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #contors closed loop aaroun white areas 
    if len(contors) == 0 :
        cv2.imshow('Camera', frame)
        continue 
    largest = max(contors, key =cv2.contourArea)
    if cv2.contourArea(largest) > 4500 :
        cv2.imshow('Camera', frame)
        
        #OBJECT TRACKING
        M = cv2.moments(largest) 
        if M['m00'] != 0 :
            cx = int(M['m10'] / M['m00']) #m10 is sum of movement area along x
            cy = int(M['m01'] / M['m00']) #dividing ny the area gives us center of movement
            cv2.circle(frame, (cx,cy), 8, (0, 0, 255), -1) #disk of radius 8 overidden with red
            if smooth_centroid is None : 
                smooth_centroid = (cx, cy)
            else : 
                sx = int(delta*smooth_centroid[0] + (1-delta)*cx)
                sy = int(delta*(smooth_centroid[1])+ (1-delta)*cy)
                smooth_centroid = (sx,sy)

            if last_centroid is not None : 
                cv2.line(frame, last_centroid, (cx, cy), (255, 0, 0), 2 ) #secant from last com to current
            last_centroid = (cx, cy)

    cv2.imshow('Camera', frame) #creates window to display current array
    cv2.imshow('Motion Mask', thresh)
    cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)      # raw (yellow)
    cv2.circle(frame, smooth_centroid, 8, (0, 0, 255), -1) # smooth (red)

    vx = smooth_centroid[0] - last_centroid[0]
    vy = smooth_centroid[1] - last_centroid[1]
    speed = (vx**2 + vy**2)**.5

    angle = math.atan2(vy,vx)

    if cv2.waitKey(1) & 0xFF == ord('q') : 
        break #exits loop when press q

cap.release() #returning the hardware 
cv2.destroyAllWindows()
