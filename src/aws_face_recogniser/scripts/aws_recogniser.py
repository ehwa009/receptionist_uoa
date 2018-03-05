#!/usr/bin/env python
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import threading
import rospkg
import boto3
import json

class image_converter:
    
    def __init__(self):
        self.face_pub = rospy.Publisher("/receptionist_face_input",String, queue_size=10)
        self.image = None
        self.bridge = CvBridge()
        #self.image_sub = rospy.Subscriber("/camera/rgb/image_raw",Image,self.callback)
        self.image_sub = rospy.Subscriber("/camera/image_raw", Image, self.callback)

        self.client = boto3.client('rekognition')        
        self.path = rospkg.RosPack().get_path('aws_face_recogniser') + "/scripts/"

        self.face_cascade = cv2.CascadeClassifier(self.path + 'haarcascade_frontalface_alt.xml')           
        self.label = "loading..."

    def callback(self, data):
        try:
          cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
          print(e)

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.5,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        for (x,y,w,h) in faces:
            cv2.rectangle(cv_image,(x,y),(x+w,y+h),(255,0,0),2)
            cv2.putText(cv_image, self.label ,(x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)

        self.image = cv_image

        cv2.imshow("Image window", cv_image)
        cv2.waitKey(3)

    def aws_recognise(self):
        t = threading.Timer(1.0, self.aws_recognise)
        t.daemon = True
        t.start()

        if self.image != None:
            #img_str = cv2.imencode('.png', self.image)[1].tostring()
            
            # Image for jpg
            # Added by Eddie
            img_str = cv2.imencode('.jpg', self.image)[1].tostring()
            response = self.client.search_faces_by_image(
                CollectionId='receptionist_collection',
                Image={'Bytes': img_str,},
                MaxFaces=5,
#                FaceMatchThreshold=...
            )
            matches = response.get("FaceMatches")
            
            if len(matches) > 0:
                person_id = matches[0].get("Face").get("ExternalImageId")
                conf = str(matches[0].get("Face").get("Confidence"))
                self.label =  "Found: " + person_id + " - conf: " + conf
                self.face_pub.publish("detected:" + person_id + "&conf:" + conf);
            else:
                self.label = "No faces found"
        else:
            print "image undefined"

def main(args):
  ic = image_converter()
  ic.aws_recognise()
  rospy.init_node('image_converter', anonymous=True)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)