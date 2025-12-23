    overview
i would like this project to use my macbooks camera and microphone to track and save skatebording clips. so far it utilizes my macs camera, detects occuring motion, and finds its the contours of it provided its within my threshold.
 
    reminders/learing
-(venv) before terminal prompt means inside sandbox
-open cv is vison library to work with frames as numpy arrays 
-heightxwidthxchannels is 3d numerical array 
-vosk takes raw live audio samples from sounddevice (mac microphone) and matches them against launguge models quickly
-if the differnce in sucsessive frames is big eneough, something moved 
-each frame is a numpy array, each pixel is of the form [B,G,R]. when we 'draw' on the frame, we are mutating the array (setting one color to 255, others to 0)
-keyword(ctrl+ shift+ space : gives parameters 




