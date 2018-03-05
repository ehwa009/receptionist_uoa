#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import signal

def callback(data):
    cmd = data.data
    rospy.loginfo(rospy.get_caller_id() + ": I heard %s", cmd)
    
def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/receptionist_face_train", String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
