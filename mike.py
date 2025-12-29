import numpy as np #audio comes in arrays of floats 
import sounddevice as sd 
import json
from vosk import Model, KaldiRecognizer 
import queue
import time

q =queue.Queue() #auido inbox, holds so the callback can inspect on own time
model = Model('vosk_model') #trained speech knowladge 
recognizer = KaldiRecognizer(model, 16000) #streaming decoder, using model knowladge expecting 16000 samples/s

def callback(indata, frames, time, status) :
    q.put(indata.copy()) #avioding corruption
    with sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=callback) : #opens mic, starts streamning, callback is the receiver
        print('listening, press ctrl c to stop')
        try :
            while True :
                time.sleep(.05)
        except KeyboardInterrupt :
            print('stopped')
    if not q.empty() :
        data = q.get() #oldest auido chunk
        if recognizer.AcceptWaveform(data.tobytes()) : #a word is finished
            result = json.loads(recognizer.Result())
            if 'yes'or 'lets'or 'go' or 'yeah' in result.split :
                print('yes')
