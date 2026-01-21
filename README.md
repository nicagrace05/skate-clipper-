# 🛹 Skate Clipper: use cleaned_up.py

Voice activated skate session recorder that automatically saves clips when you land tricks! Make sure your device has a microphone and camera. She's a bit activation happy during conversations, but better safe than sorry!

## Getting Started 

- Load the code and make + activate a virtual environment
- Use requirements.txt to load packages 
- Open FaceTime for camera access, may need to adjust system settings on your computer 
- Make a folder on your desktop called skate_sessions or edit line 14 for a path

## Customise

- **line 14:** `base_dir = Path.home() / 'path for where you want your clips saved'`
- **line 28:** `clip_t = the clip length you want`
- **line 31:** `cooldown = 7` seconds between allowed saves (recommended at least 3)
- **line 77:** `clip = clip.fx(vfx.speedx, (the speed you want))` (.5 is half speed, 1 is normal)
- **line 100:** `if any(word in text for word in ["keyword", "another"]):` trigger words

## To Use

Position your camera to capture your skate spot

Skate and land tricks! When you land something, say your keywords.

The program will:
- Save the last few seconds of footage
- Store it in a timestamped session folder
- Print a confirmation in the terminal

**PRESS Q TO EXIT** - This will:
- Close all systems and make a slow-mo edit of all your clips
- Save it as the last item in your folder!

---

Use however you please. Pull requests welcome, maybe for help with a crop in the 'other' folder? 

Made by a skater for skaters, GO LAND THAT SHI FAMMMMMMM 🛹