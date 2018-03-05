#!/usr/bin/env python
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import time
import threading

# from __future__ import print_function

class image_converter:

  def __init__(self):
    self.refPt = [(0, 0),(0, 0)]
    self.cropping = False
    self.bridge = CvBridge()
    # self.image_sub = rospy.Subscriber("/camera/rgb/image_raw",Image,self.callback)
    self.image_sub = rospy.Subscriber("/camera/image_raw", Image, self.callback)
    self.croppedImage = None

  def capture(self):
    for x in range(0, 5):
      print("captured")
      cv2.imwrite("face-" + str(int(time.time())) + ".jpg", self.croppedImage)
      time.sleep(1)

  def click_and_crop(self, event, x, y, flags, param):
    # grab references to the global variables
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
      self.refPt = [(x, y)]
      self.cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
      # record the ending (x, y) coordinates and indicate that
      # the cropping operation is finished
      self.refPt.append((x, y))
      self.cropping = False
      threading.Timer(1.0, self.capture).start()

  def callback(self,data):
    try:
      cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)

    (rows,cols,channels) = cv_image.shape
    if cols > 60 and rows > 60 :
      cv2.circle(cv_image, (50,50), 10, 255)
    
    cv2.setMouseCallback("Image window", self.click_and_crop)
    if (len(self.refPt) == 2):
      cv2.rectangle(cv_image, self.refPt[0], self.refPt[1], (0, 255, 0), 2)
      self.croppedImage = cv_image[self.refPt[0][1]:self.refPt[1][1], self.refPt[0][0]:self.refPt[1][0]]

    cv2.imshow("Image window", cv_image)
    cv2.waitKey(3)

def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)

  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)