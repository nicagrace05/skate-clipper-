import cv2
import os
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
stopping = False 
last_time = 0
cooldown = 7 #locks saving for 7s
maxw = 0
maxh = 0 

def Callback(indata, frames, time, status) : #sounddevice calls this funtion, not my code, dont worry about undefined varibles
    if stopping :
        return
    q.put(indata.copy()) #avioding corruption

q =queue.Queue() #auido inbox, holds so the callback can inspect on own time
model = Model('vosk_model') #trained speech knowladge 
recognizer = KaldiRecognizer(model, 16000) #streaming decoder, using model knowladge expecting 16000 samples/s
stream = sd.InputStream(
    channels=1,
    samplerate=16000,
    blocksize=800,
    dtype='int16',
    callback=Callback) #we dont call Callback, simply pass it to sounddevice
stream.start() 
print('listening for yes, lets go')

def Save_clip(frames) : #expects tuples
    #global triggered, buffer, maxw, maxh
    if len(frames) == 0 :
        print('aint no frames round here cuh')
        return
    # cropw = maxw
    # croph = maxh
    # if cropw == 0 or croph == 0 :
    #     print('sum is sus round these parts...')
    #     return 
    # else :
    h0, w0, _ = frames[0][1].shape
    filename = f'/Users/nicarobertson/Desktop/skate-clipper-/clips/clip_{int(time.time())}.mp4'
    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), 30, (w0,h0))
    if not out.isOpened() :
        print('video writer failed')
        return
    # for _, frame, centroid in frames :
    #     if centroid is None : 
    #         continue 
    #     x1 = sx - cropw // 2
    #     y1 = sy - croph // 2
    #     x2 = sx + cropw // 2
    #     y2 = sy + croph // 2    
    #     H,W,_ = frame.shape
    #     x1c, y1c = max(0, x1), max(0, y1)
    #     x2c, y2c = min(W, x2), min(H, y2)
    #     crop = frame[y1c:y2c, x1c:x2c]
    #     canvas = np.zeros((croph, cropw, 3), dtype=np.uint8)
    #     ch, cw, _ = crop.shape
    #     y_off = (croph - ch) // 2
    #     x_off = (cropw - cw) // 2
    #     canvas[y_off:y_off+ch, x_off:x_off+cw] = crop
    for _, frame, _ in frames :
        out.write(frame)
    out.release()
    print('saved! steeeeeeeeeee', filename)
    # maxh = 0
    # maxw = 0

while True :
    now = time.time()
    ret, frame = cap.read() #frame is HxWx3, for BGR channels, vals from 0-255
    if not ret : 
        print('failed to get frame')
        break

        #MOTION THRESHOLD
    raw = frame.copy()
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
        continue #efficientcy
    largest = max(contors, key =cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(largest) #both instantious: (x,y) is top left corner,(w,h) is dimesions of box 
    cv2.rectangle(frame, (x,y,), (x+w, y+h), (0,255,0), 2)

    #CENTER OF MOTION, SMOOTHING TRACKING
    # M = cv2.moments(largest) 
    # if M['m00'] != 0 :
    #     cx = int(M['m10'] / M['m00']) #m10 is sum of movement area along x
    #     cy = int(M['m01'] / M['m00']) #dividing ny the area gives us center of movement
    #     cv2.circle(frame, (cx,cy), 8, (0, 0, 255), -1) #disk of radius 8 overidden with red
    #     if smooth_centroid is None : 
    #         smooth_centroid = (cx, cy) 
    #     else : 
    #         sx = int(delta*smooth_centroid[0] + (1-delta)*cx)
    #         sy = int(delta*(smooth_centroid[1])+ (1-delta)*cy)
    #         smooth_centroid = (sx,sy)
    #     sx,sy = smooth_centroid 

    #     if smooth_w is None :
    #         smooth_w, smooth_h = w,h
    #     else :
    #         smooth_w = int(delta * smooth_w + (1-delta)*w)
    #         smooth_h = int(delta * smooth_h + (1-delta)*h)

    #     x1 = sx - smooth_w // 2 #smoothed centroid controls boxes motion, contour controls size
    #     x2 = sx + smooth_w // 2
    #     y1 = sy - smooth_h // 2
    #     y2 = sy + smooth_h // 2

    #     H, W, _ = frame.shape 
    #     x1, y1 = max(0, x1), max(0, y1)
    #     x2, y2 = min(W, x2), min(H, y2)
    #     (x,y,w,h) = cv2.boundingRect(largest)
    #     maxw = max(maxw, w)
    #     maxh = max(maxh, h)
    #     crop = frame[y1:y2,x1:x2]
    cv2.imshow('camera_raw', raw)

                    #MIC AND WORD RECOGNITION
    while not q.empty() :
        data = q.get() #drain queue
        if recognizer.AcceptWaveform(data.tobytes()):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            if any(word in text for word in ["yes", "go", "yeah", "lets"]):
                triggered = True
                print('saving...')

    cutoff = now - clip_t
    buffer.append((now, raw, smooth_centroid)) #append accepts 1 argument, make er a tuple
    buffer = [(t,f,c) for t, f, c in buffer if t >= cutoff] #temporary memory updates every ideration
    
    if triggered and (now - last_time) > cooldown :
        Save_clip(buffer)
        buffer.clear()
        last_time = now
        triggered = False

    if cv2.waitKey(1) & 0xFF == ord('q') : 
        stopping = True
        stream.stop()
        stream.close()
        time.sleep(.1)
        cap.release() #returning the hardware 
        cv2.destroyAllWindows()
        print('stopped fam')
        break #exits loop when press q

#DEBUGGING
#cv2.imshow('Camera', frame) #creates window to display current array
#cv2.imshow('Motion Mask', thresh)
#cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)      # raw (yellow)
#cv2.circle(frame, smooth_centroid, 8, (0, 0, 255), -1) # smooth (red)