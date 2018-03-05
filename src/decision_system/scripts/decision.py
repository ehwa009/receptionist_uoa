#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String

decision_pub = rospy.Publisher('/receptionist_decision_input', String, queue_size=10)

def perceptionCallback(data):
    rospy.loginfo("you said:%s", data.data)
    sys.stdout.flush()
    decision_pub.publish(data.data)
    
def decisionCallback(data):
    rospy.loginfo("receptionist says: " + data.data)
    sys.stdout.flush()

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/receptionist_perception_output", String, perceptionCallback)
    rospy.Subscriber("/receptionist_decision_response", String, decisionCallback)
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
