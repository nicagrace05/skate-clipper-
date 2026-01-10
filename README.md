    overview
i would like this project to use my macbooks camera and microphone to track and save skatebording clips. 
so far it utilizes my macs camera and mic, to listen for keywords and save a 7 second clip before that to the file 'clips' in the repo. eventually i want to crop each frame around the motion and maybe slow the fps, but im running into issues with defining a center of motion to crop around that is consistent enough to not through errors when cropping around.
 
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
- vosk recognition is best when a gap suggests an end to a sentace, in this case acceptwaveform(audio) retutrns True
- break doesnt work inside funtions cuh, you can exit by returning
- to save a file we need all frame sizes to be equal 



