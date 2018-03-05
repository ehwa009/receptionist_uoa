#!/usr/bin/env python
# license removed for brevity
import rospy
from face_recognition.msg import FRClientGoal
import time

def talker():
    ## give warnings before running
    print("Make sure Fserver and Fclient are running.")
    print("rosrun face_recognition Fserver")
    print("rosrun face_recognition Fclient")
    print("Ctrl Z to quit")

    pub = rospy.Publisher('fr_order', FRClientGoal, queue_size=1)
    rospy.init_node('face_trainer', anonymous=True)
    r = rospy.Rate(15)

    while not rospy.is_shutdown():
        print("Please enter choice: (d=detect, r=reload, t=train, q=quit)")
        choice = raw_input("")
        if choice == "q" :
            break
        elif choice == "r":
            pub.publish(3, "none")
        elif choice == "d":
            pub.publish(1, "none")
        elif choice == "t":
            print("Please sit 0.5m-1m back from camera")
            print("Press enter your name (no spaces please) to start automatic 15 second record")
            name = raw_input("")
            pub.publish(2, name)
            time.sleep(15)
            pub.publish(3, "none")

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
