import numpy as np
import cv2
import sounddevice as sd
from vosk import Model

print("NumPy version:", np.__version__)
print("OpenCV version:", cv2.__version__)
print("Sounddevice OK:", sd.query_devices() is not None)
print("Vosk OK")

