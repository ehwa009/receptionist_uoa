#!/usr/bin/env python
import rospy
import pyaudio
import wave
import audioop
from collections import deque
import os
import urllib2
import urllib
import time
import math
import sys
import base64
import array
import requests
import json
import thread
from std_msgs.msg import String
import signal
from wit import Wit
import houndify
from Microsoft_ASR import Microsoft_ASR
import time

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 1  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.

BUFFER_SIZE = 512
WAVE_OUTPUT_FILENAME = "file.wav"

client = houndify.StreamingHoundClient("Af_ZKEcCOrVcAvjFnbBmcg==", "l2jjCCDZTpLVzOKmzuzszUaQx1BhCNwLnapBU2RuIxrR16oby6G8tw9UXWtfhujvAd3QI_yh80lpwccbRGSLew==", "test_user")
client.setLocation(-36.865771, 174.772555)
client.setHoundRequestInfo('PartialTranscriptsDesired', False)
                  # of the phrase.
pub = rospy.Publisher('/receptionist_speech_input', String, queue_size=10)

# phrases = [
#         "I need to see", "I want to see", "I have to see", "meet", "see", "visit", "meeting", "appointment", "thank you", "please", "yes", "no", "ok", "toilet", "bathroom", "stairs", "elevator", "lifts", "robotics lab", "power electronics lab", "control systems lab", "radio systems lab",
#         "bruce", "catherine", "wesley", "bob", "ho seok", "doctor", "watson", "macdonald" "professor", "university", "engineering", "campus", "office", "parking", "park", "gate", "door", "hello", "hey", "hi"
#         "find", "locate", "directions", "building", "room", "room 903", "room 904", "ho seok", "building 903", "building 904", "fung yang", "souriya"
#     ]

def audio_int(num_samples=50):
    """ Gets average audio intensity of your mic sound. You can use it to get
        average intensities while you're talking and/or silent. The average
        is the avg of the 20% largest intensities recorded.
    """

    print "Getting intensity values from mic."
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
    
    print " Finished "
    print " Average audio intensity is ", r
    
    threshold = r + 2000
    
    print " Setting threshold to ", threshold
    
    stream.close()
    p.terminate()
    
    return threshold

def listen_for_speech(threshold, num_phrases=-1):
    """
    Listens to Microphone, extracts phrases from it and sends it to 
    Google's TTS service and returns response. a "phrase" is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite). 
    """

    #Open stream
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print "* Listening mic. "
    
    sys.stdout.flush()
    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    
    slid_win = deque(maxlen=SILENCE_LIMIT * rel)
    prev_audio = deque(maxlen=PREV_AUDIO * rel) #Prepend audio from 0.5 seconds before noise was detected
    
    started = False
    n = num_phrases
    response = []

    while not rospy.is_shutdown():
        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        
        #print slid_win[-1]
        if(sum([x > threshold for x in slid_win]) > 0):
            if(not started):
                print "Starting record of phrase"
                sys.stdout.flush()
                started = True
            audio2send.append(cur_data)
        
        elif (started is True):
            print "Finished"
            sys.stdout.flush()
            # The limit was reached, finish capture and deliver.
            raw = ''.join(list(prev_audio) + audio2send)
            # millis = int(round(time.time() * 1000))
            # print millis
            if rospy.get_param("/houndify_speech") == "yes":
                sendToHoundify(p, raw)
            
            if rospy.get_param("/wit_speech") == "yes":
                sendToWit(p, raw)

            if rospy.get_param("/bing_speech") == "yes":
                sendToBingSpeech(p, raw)
            
            if rospy.get_param("/google_speech") == "yes":
                content = base64.b64encode(raw)
                sendRequest(content)

            started = False
            slid_win = deque(maxlen=SILENCE_LIMIT * rel)
            prev_audio = deque(maxlen=0.5 * rel) 
            audio2send = []
            n -= 1
            print "Listening ..."
            sys.stdout.flush()
        
        else:
            prev_audio.append(cur_data)

    print "* Done recording"
    
    stream.close()
    p.terminate()
    sys.stdout.flush()

    return response

def sendToHoundify(audio, frames):
    createWavFile(audio, frames)
    audio = wave.open("file.wav")
    
    if audio.getsampwidth() != 2:
      print "%s: wrong sample width (must be 16-bit)" % fname

    if audio.getframerate() != 8000 and audio.getframerate() != 16000:
      print "%s: unsupported sampling frequency (must be either 8 or 16 khz)" % fname
    
    if audio.getnchannels() != 1:
      print "%s: must be single channel (mono)" % fname

    client.setSampleRate(audio.getframerate())
    samples = audio.readframes(BUFFER_SIZE)
    finished = False

    client.start(MyListener())
    
    while not finished:
      finished = client.fill(samples)
      time.sleep(0.032)     ## simulate real-time so we can see the partial transcripts
      samples = audio.readframes(BUFFER_SIZE)
      if len(samples) == 0:
        break
    
    client.finish()

def sendToBingSpeech(audio, frames):
    createWavFile(audio, frames)
    ms_asr = Microsoft_ASR()
    ms_asr.get_speech_token()
    text, confidence = ms_asr.transcribe("file.wav")
    print "Bing Response: ", text
    millis = int(round(time.time() * 1000))
    print millis
    pub.publish(text)

def sendToWit(audio, frames):
    createWavFile(audio, frames)
    client = Wit(access_token="CU77ZWXAO4STA5GEBM3VRU4UYSCEW7JI")
    resp = None
    with open(WAVE_OUTPUT_FILENAME, 'rb') as f:
      resp = client.speech(f, None, {'Content-Type': 'audio/wav'})
    print('Wit Response: ' + resp["_text"])
    pub.publish(resp["_text"])

def createWavFile(audio, frames):
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

# Send recorded audio file to Google api
def sendRequest(content):
    payload = {'config': {'encoding': "LINEAR16", "sampleRateHertz": 16000, "languageCode": "en-NZ"}, 'audio': {"content": content}}
    r = requests.post("https://speech.googleapis.com/v1/speech:recognize?key=AIzaSyCO0PuFPmLp-dxLzdgsHNe9c-A4uIvpN5Q", 
                        data=json.dumps(payload))
 #   print(r.status_code, r.reason)
    sys.stdout.flush()
    if r.json():
        transcript = r.json().get("results")[0].get("alternatives")[0].get("transcript")
        print("Google Response: " + transcript)
        pub.publish(transcript)


# Simplest HoundListener; just print out what we receive.
#
# You can use these callbacks to interact with your UI.
#
class MyListener(houndify.HoundListener):
    def onPartialTranscript(self, transcript):
        print "Partial transcript: " + transcript
    def onFinalResponse(self, response):
        print "Houndify response: " + response["AllResults"][0]["RawTranscription"]
        pub.publish(response["AllResults"][0]["RawTranscription"])
    def onError(self, err):
        print "Error: " + str(err)

if(__name__ == '__main__'):
    rospy.init_node('recogniser', anonymous=True)
    threshold = audio_int()
    print("google: " + rospy.get_param("/google_speech"))
    print("wit: " + rospy.get_param("/wit_speech"))
    print("houndify: " + rospy.get_param("/houndify_speech"))
    print("bing: " + rospy.get_param("/bing_speech"))
    
    listen_for_speech(threshold)  # listen to mic.
    rospy.spin()
    