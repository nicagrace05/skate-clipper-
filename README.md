    overview
i would like this project to use my macbooks camera and microphone to track and save skatebording clips. 
so far it utilizes my macs camera and mic, detects and crops the frame for the largest occuring motion, listens for my favorite celebration words. if the motion threshold is hit and words are recognized, a 5 second clip before the word detection is saved to a folder on my desktop. still buggy doe
 
    reminders/learing
-   (venv) before terminal prompt means inside sandbox
-   open cv is vison library to work with frames as numpy arrays 
-   heightxwidthxchannels is 3d numerical array 
-   vosk takes raw live audio samples from sounddevice (mac microphone) and matches them against launguge models quickly
-   if the differnce in sucsessive frames is big eneough, something moved 
-   each frame is a numpy array, each pixel is of the form [B,G,R]. when we 'draw' on the frame, we are mutating the array (setting one color to 255, others to 0)
-   keyword(ctrl+ shift+ space : gives parameters 
-  vosk model zip is collection of trained neural network weights vosk can read
- all caps on a varible signifys its inteneded to not be changed. objects commonly upercase until specifcation. some library funtions imported from c++ like KaldiRecognizer, need exact capitilzation
- in real time systems, sensors can push data in the background without the prosesses being in the main loop 
- camera and mic have differnt clocks cause they accept diffent sample frequancies, we need one global time.time()



