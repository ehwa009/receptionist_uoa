#!/usr/bin/env python
import rospy
import pyaudio
import wave
import time
import pyttsx
from gtts import gTTS 
import subprocess

if(__name__ == '__main__'):
    # engine = pyttsx.init()
    # engine.setProperty('voice', 'english+f1')
    # engine.say('Hi, I am ever robot receptionist. Welcome to the newmarket campus. How can I help you?')
    # engine.runAndWait()

    tts = gTTS(text='Hi, I am ever robot receptionist. Welcome to the newmarket campus. How can I help you?', lang='en')
    tts.save("speech.mp3")
    subprocess.Popen(['mpg123','speech.mp3', '-vn'])