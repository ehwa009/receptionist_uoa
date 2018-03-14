import rospy
from std_msgs.msg import String

import importlib
import os
import logging
import tempfile
import signal
import shutil
import time
import sys
import threading
import json
import optparse
import email
import subprocess
import hashlib
from future.builtins import bytes

import yaml
import requests
import coloredlogs

import alexapi.config
import alexapi.tunein as tunein
import alexapi.capture
import alexapi.triggers as triggers
from alexapi.exceptions import ConfigurationException
from alexapi.constants import RequestType, PlayerActivity

def talker():
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
