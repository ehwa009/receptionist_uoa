#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String
import pyttsx
from gtts import gTTS 
import subprocess
import boto3
from contextlib import closing

client = boto3.client('polly')

def textReceivedCallback(data):
    text = data.data
    if rospy.get_param("/python_tts") == "yes":
        engine = pyttsx.init()
        engine.setProperty('voice', 'english+f1')
        engine.say(text)
        engine.runAndWait()
    if rospy.get_param("/google_tts") == "yes":
        tts = gTTS(text=text, lang='en')
        tts.save("speech.mp3")
        subprocess.Popen(['mpg123','speech.mp3', '-vn'])
    if rospy.get_param("/aws_polly_tts") == "yes":
        response = client.synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            TextType='text',
            VoiceId='Joanna'
        )
        with closing(response["AudioStream"]) as stream:
            output = "speech.mp3"
            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
        subprocess.Popen(['mpg123','speech.mp3', '-vn'])

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    if rospy.get_param("/python_tts") == "yes":
        rospy.logwarn("Using python TTS")
    if rospy.get_param("/google_tts") == "yes":
        rospy.logwarn("Using google TTS")
    if rospy.get_param("/aws_polly_tts") == "yes":
        rospy.logwarn("Using AWS Polly TTS")
    sys.stdout.flush()

    rospy.Subscriber("/receptionist_decision_response", String, textReceivedCallback)
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
