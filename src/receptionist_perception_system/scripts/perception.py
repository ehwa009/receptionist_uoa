#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String

face_pub = rospy.Publisher('/receptionist_face_train', String, queue_size=10)
perception_pub = rospy.Publisher('/receptionist_perception_output', String, queue_size=10)

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + ": I heard %s", data.data)
    cmd = data.data
    if cmd == "train": 
        face_pub.publish("train")
    elif cmd.startswith("capture"): #param1 = label
        label = cmd.split("?")[1]; # eg. capture?wesley (means capture face with label wesley)
        print("capture cmd sent with label: " + label)

def speechInputCallback(data):
    rospy.loginfo("detectedspeech:%s", data.data)
    perception_pub.publish(data.data)
    sys.stdout.flush()
    
def faceInputCallback(data):
    #rospy.loginfo("detectedface:%s", data.data)
    sys.stdout.flush()
    perception_pub.publish("recognised face of " + data.data)

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/receptionist_perception_action", String, callback)
    rospy.Subscriber("/receptionist_speech_input", String, speechInputCallback)
    rospy.Subscriber("/receptionist_face_input", String, faceInputCallback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
