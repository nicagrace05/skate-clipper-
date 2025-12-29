import cv2
import numpy as np
import time
import sounddevice as sd 
import json
from vosk import Model, KaldiRecognizer 
import queue

#CAMERA ACSESS
cap = cv2.VideoCapture(0) #zero is first available camera device, camera app must be open
if not cap.isOpened() : 
    raise RuntimeError('couldnt open camera') #error with presmissions 

first_frame = None 
smooth_centroid = None
smooth_w = None
smooth_h = None 
alpha = .02
delta = .6 #greater val -> smoother,slower motion tracking
buffer = []
triggered = False 
clip_t = 5

def Callback(indata, frames, time, status) : #sounddevice calls this funtion, not my code, dont worry about undefined varibles
    q.put(indata.copy()) #avioding corruption
q =queue.Queue() #auido inbox, holds so the callback can inspect on own time
model = Model('vosk_model') #trained speech knowladge 
recognizer = KaldiRecognizer(model, 16000) #streaming decoder, using model knowladge expecting 16000 samples/s
stream = sd.InputStream(samplerate=16000, channels=1, callback=Callback) #we dont call Callback, simply pass it to sounddevice
stream.start() 
print('listening for yes, lets go')
def Save_clip(frames) : #expects tuples
    if len(frames) == 0 :
        return
    h, w, _ = frames[0][1].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    filename = f'/Users/nica/Desktop/clips/clip_{int(time.time())}.mp4'
    out = cv2.VideoWriter(filename, fourcc, 30, (w,h))
    for _, f in frames :
        out.write(f)
    out.release()
    print('saved', filename)
    global triggered, buffer 
    triggered = False
    buffer = []

while True :
    now = time.time()
    ret, frame = cap.read() #frame is HxWx3, for BGR channels, vals from 0-255
    if not ret : 
        print('failed to get frame')
        break

        #MOTION THRESHOLD
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #motion is soley about intensity here
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0) #big blur to filter out noise
    if first_frame is None :
        first_frame = gray_blur.copy()
        continue 
    first_frame = cv2.addWeighted(gray_blur, alpha, first_frame, 1-alpha, 0) #exponetial background averaging keeps only motion relavent agaisnt stationary background
    frame_delta = cv2.absdiff(first_frame, gray_blur) #the differences in frames visualized in pixels (white=motion)
    _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY) #defining what is considered movement
    thresh = cv2.dilate(thresh, None, iterations = 2)
    contors, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #contors closed loop aaroun white areas 
    if len(contors) == 0 :
        cv2.imshow('camera', frame)
        continue #efficientcy
    largest = max(contors, key =cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(largest) #both instantious: (x,y) is top left corner,(w,h) is dimesions of box 
    cv2.rectangle(frame, (x,y,), (x+w, y+h), (0,255,0), 2)

    #CENTER OF MOTION, SMOOTHING TRACKING
    M = cv2.moments(largest) 
    if M['m00'] != 0 :
        cx = int(M['m10'] / M['m00']) #m10 is sum of movement area along x
        cy = int(M['m01'] / M['m00']) #dividing ny the area gives us center of movement
        cv2.circle(frame, (cx,cy), 8, (0, 0, 255), -1) #disk of radius 8 overidden with red
        if smooth_centroid is None : 
            sx, sy = cx, cy
        else : 
            sx = int(delta*smooth_centroid[0] + (1-delta)*cx)
            sy = int(delta*(smooth_centroid[1])+ (1-delta)*cy)
            smooth_centroid = (sx,sy)

        if smooth_w is None :
            smooth_w, smooth_h = w,h
        else :
            smooth_w = int(delta * smooth_w + (1-delta)*w)
            smooth_h = int(delta * smooth_h + (1-delta)*h)

        x1 = sx - smooth_w // 2 #smoothed centroid controls boxes motion, contour controls size
        x2 = sx + smooth_w // 2
        y1 = sy - smooth_h // 2
        y2 = sy + smooth_h // 2

        H, W, _ = frame.shape 
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(W, x2), min(H, y2)
        crop = frame[y1:y2,x1:x2]

                    #MIC AND WORD RECOGNITION
        while not q.empty() : #empties q each frame 
            data = q.get() #oldest auido chunk
            if recognizer.AcceptWaveform(data.tobytes()) : #a word is finished
                result = json.loads(recognizer.Result())
                text = result.get('text', '').lower()
                if any(word in text for word in['yes', 'lets', 'go', 'yeah']) :
                    triggered = True
                    print('grarly shit bruh, saving clip!')
        if crop.size > 0 :
            cv2.imshow('camera', frame)
            buffer.append((now, crop))
        if crop.size == 0 :
            continue

        cutoff = now - clip_t
        buffer = [(t,f) for t, f in buffer if t >= cutoff] #temporary memory updates every ideration

        if triggered :
            Save_clip(buffer)

    if cv2.waitKey(1) & 0xFF == ord('q') : 
        break #exits loop when press q

stream.stop()
stream.close()
cap.release() #returning the hardware 
cv2.destroyAllWindows()
print('stopped fam')

#DEBUGGING
#cv2.imshow('Camera', frame) #creates window to display current array
#cv2.imshow('Motion Mask', thresh)
#cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)      # raw (yellow)
#cv2.circle(frame, smooth_centroid, 8, (0, 0, 255), -1) # smooth (red)