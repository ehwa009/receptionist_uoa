#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import signal
import sys
import json
import uuid
import boto3
import subprocess
from contextlib import closing
import apiai
import os

CLIENT_ACCESS_TOKEN = os.environ['API_AI_CLIENT_ID']
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
session_id = uuid.uuid4().hex
# pub = rospy.Publisher('/receptionist_decision_response', String, queue_size=10)

client = boto3.client('lex-runtime')
session_id = uuid.uuid4().hex
session_attributes = {}
pub = rospy.Publisher('/receptionist_nlp_response', String, queue_size=10)

def speechReceivedCallback(data):
    sys.stdout.flush()
    
    # do nlp ai calls here
    global session_attributes

    # AWS lex
    if rospy.get_param("/lex_decision") == "yes":
        response = client.post_content(
            botName='ReceptionistNLP',
            #botName='ReceptionistNLPSec',
            botAlias='Test',
            #botAlias='Eddie',
            userId=session_id,
            contentType='text/plain; charset=utf-8',
            sessionAttributes=session_attributes,
            accept='text/plain; charset=utf-8',
            inputStream=data.data
        )
        intent = response.get("intentName") if response.get("intentName") else ""
        slots = response.get("slots") if response.get("slots") else "{}"
        message = response.get("message") if response.get("message") else ""
        
        pub.publish(intent + "#" + str(slots) + "#" + message + "#" + data.data)

    # Google api.ai
    if rospy.get_param("/api_ai_decision") == "yes":
        request = ai.text_request()
        request.lang = 'en'  # optional, default value equal 'en'
        request.session_id = session_id
        request.query = data.data
        response = request.getresponse()
        responseMap = json.loads(response.read())
        intent = responseMap["result"]["metadata"]["intentName"]
        slots = responseMap["result"]["parameters"]
        message = responseMap["result"]["fulfillment"]["speech"]
        
        pub.publish(intent + "#" + str(slots) + "#" + message + "#" + data.data)

def listener():
    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("/receptionist_decision_input", String, speechReceivedCallback)

    rospy.logwarn("lex: " + rospy.get_param("/lex_decision"))
    rospy.logwarn("api_ai: " + rospy.get_param("/api_ai_decision"))
    
    sys.stdout.flush()
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    print("nlp node started")
    listener()