import cv2
import os
import numpy as np
import time
import sounddevice as sd 
import json
from vosk import Model, KaldiRecognizer 
import queue
from datetime import datetime
from pathlib import Path
from moviepy.editor import VideoFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

base_dir = Path.home() /'Desktop'/'skate_sessions'
base_dir.mkdir(exist_ok=True)

SESSION_NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
SESSION_DIR = base_dir / SESSION_NAME
SESSION_DIR.mkdir()

#CAMERA ACSESS
cap = cv2.VideoCapture(0) #zero is first available camera device, camera app must be open
if not cap.isOpened() : 
    raise RuntimeError('couldnt open camera') #error with presmissions 

buffer = []
triggered = False 
clip_t = 4
stopping = False 
last_time = 0
cooldown = 7 #locks saving for 7s, prevents against spam on one instance of a word
saved_clips = []
clip_count = 0

def Callback(indata, frames, time, status) : #sounddevice calls this funtion, not my code, dont worry about undefined varibles
    if stopping :
        return
    q.put(indata.copy()) #avioding corruption

q = queue.Queue() #auido inbox, holds so the callback can inspect on own time
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
    if len(frames) == 0 :
        print('aint no frames round here cuh')
        return
    global clip_count
    clip_count += 1
    filename = SESSION_DIR / f"clip_{clip_count}.mp4"
    filename = str(filename)
    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920,1080))
    if not out.isOpened() :
        print('video writer failed')
        return
    for _, frame in frames :
        out.write(frame)
    out.release()
    print('saved! steeeeeeeeeee', filename)
    saved_clips.append(filename) #'remembers' current session only

def make_session_edit(): 
    if len(saved_clips) == 0:
        print('lock in bro wyd???')
        return
    clips = []
    for path in saved_clips:
        clip = VideoFileClip(path)
        clip = clip.fx(vfx.speedx, 0.7) # slow motion: 0.5 = half speed
        clips.append(clip)
    final = concatenate_videoclips(clips, method="compose")
    outname = SESSION_DIR / "session_edit.mp4"
    final.write_videofile(str(outname), fps=30)
    print("Session edit saved to:", outname)

while True :
    now = time.time()
    ret, frame = cap.read() #frame is HxWx3, for BGR channels, vals from 0-255
    if not ret : 
        print('failed to get frame')
        break
    frame = cv2.resize(frame, (1920, 1080)) #resize to fit videowriteer
    raw = frame.copy()
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
    buffer.append((now, raw)) #append accepts 1 argument, make er a tuple
    buffer = [(t, f) for t, f in buffer if t >= cutoff] #temporary memory updates every ideration
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
        make_session_edit()
        break #exits loop when press q