#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import signal
import subprocess

def init():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    # call rostopic publish
    subprocess.Popen("rostopic pub -1 /Procrob/fr_order face_recognition/FRClientGoal -- 1 'none'", shell=True)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    init()
