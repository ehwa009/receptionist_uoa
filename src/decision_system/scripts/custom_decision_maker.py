#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String

pub = rospy.Publisher('/receptionist_decision_response', String, queue_size=10)
state = ""
personMeetng = ""
userName = ""
userPlace = ""

def nlpCallback(data):
    global state, personMeeting, userName, userPlace
    
    rospy.logerr(data.data)
    sys.stdout.flush()
    
    # Get intent information from api.ai or lex
    arr = data.data.split("#")

    intentName = arr[0]
    slots = eval(arr[1])
    message = arr[2]
    inputTranscript = arr[3]

    rospy.logwarn(message)

    # first check single phrase responses
    if (state == "askingName" and not intentName == "NameIntent"):
        userName = inputTranscript
        send("Where should I say you are coming from?")
        state = "askingComingFrom"
        return
    elif (state =="askingComingFrom" and not intentName == "ComingFromIntent"):
        userPlace = inputTranscript
        send("Thanks, " + userName + " from " + userPlace + ". Please take a seat while I send an email to " + personMeeting + " about your arrival.")
        reset()
        return

    # first check if the nlp provider has given us a message or prompt e.g. lex prompts
    if message:           
        send(message)
    
    elif intentName == "EverWelcome": ## now check if our intents are matched
        send("Hi, I am Ever Robot Receptionist. Welcome to the Newmarket Campus. How can I help you?")
    
    elif intentName == "RecognisedFace": ## now check if our intents are matched
        person = slots.get("Person")
        userName = person
        
        send("Hi " + person + ", I am Ever Robot Receptionist. Welcome to the Newmarket Campus. How can I help you?")
    
    elif intentName == "EverThankYou":   
        send("No problem. Is there anything else I can help you with?")
    
    elif intentName == "Meeting":
        person = slots.get("Contact")
        send("Sure, do you have an appointment with " + person + "?")
        personMeeting = person
        state = "meeting"
    
    elif intentName == "CustomYes":
        if state == "meeting":
            send("Ok, do you know where to find " + personMeeting)
            state = "findPerson"
        elif state == "findPerson":
            send("Ok, have a nice day. Thank you for using Ever Robot receptionist.")
        else:
            didNotUnderstand()
    
    elif intentName == "CustomNo":
        if state == "meeting":
            if userName != "":
                send("Where should I say you are coming from?")
                state = "askingComingFrom"
            else:
                send("Ok, could I please get your name?")
                state = "askingName"
        elif state == "findPerson":
            send("You may find " + personMeeting + " straight down the corridor in the ECE staff offices")
            reset()
        else:
            didNotUnderstand()
    
    elif intentName == "NameIntent":
        if personMeeting == "":
            send("Sorry, I did not understand. How can I help you?")
        else:
            userName = slots.get("Name")
            send("Where should I say you are coming from?")
            state = "askingComingFrom"
    
    elif intentName == "ComingFromIntent":
        if personMeeting == "" or userName == "":
            send("Sorry, I did not understand. How can I help you?")
        elif not slots.get("Place") and not slots.get("PlaceCity"):
            send("Sorry, where should I say you are coming from?")
        else:
            userPlace = slots.get("Place") if slots.get("Place") else slots.get("PlaceCity")
            if type(userPlace) is dict:
                userPlace = userPlace.values()[0]
            send("Thanks, " + userName + " from " + userPlace + ". Please take a seat while I send an email to " + personMeeting + " about your arrival.")
            reset()
    
    elif intentName == "FindLocation":
        location = slots.get("Location")
        send("You may find " + location + " straight down the corridor and on the left.")
    
    else:
        didNotUnderstand()


def didNotUnderstand():
    send("Sorry, I did not understand. Could you please clarify?")


def reset():
    global state, personMeeting, userName, userPlace
    state = ""
    personMeeting = ""
    userName = ""
    userPlace = ""

def send(text):
    pub.publish(text)

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/receptionist_nlp_response", String, nlpCallback)
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
