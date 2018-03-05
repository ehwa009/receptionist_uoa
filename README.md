# Receptionist Ever Project

## Requirements
- Ubuntu 14.04 (or higher)
- ROS (jade or higher)
- OpenCV (2.4 or higher)
- Python and Pip installer
- Google developer account (for spee
- c++ compiler
- XBox 360 or Asus XtionPro camera 
- OpenNI for webcam integration (alternatively any video stream can be used but it will need be redirected to /camera/raw)
- AWS account (for lex, AWS face recognition)
- Google developer account (for speech to text)
- API.AI account (for API.AI module)

## Setup and running
- Set up ROS workspace first
- Clone this repo into ROS workspace
- `source devel/setup.bash`
- `catkin_make`
- `roslaunch openni2_launch openni2.launch`
- `python src/gui.py`

## Dependencies
- `sudo apt-get update`
- `sudo apt-get install libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libavcodec-dev libavformat-dev libavutil-dev libswscale-dev freeglut3-dev libasound2-dev libxmu-dev libxxf86vm-dev g++ libgl1-mesa-dev libglu1-mesa-dev libraw1394-dev libudev-dev libdrm-dev gstreamer0.10-ffmpeg`
- `sudo apt-get install freeglut3-dev`
- `sudo apt-get install ros-jade-navigation`
- `sudo apt-get install ros-jade-openni2-launch`
- Check the following readme for openni2 installation if using Xbox 360 camera https://github.com/OpenNI/OpenNI/blob/master/README
- `sudo pip install boto3`
- `sudo pip install pyttsx`
- `sudo pip install gtts`
- `sudo apt-get mpg123`
- add region to aws config either in file or as env var

## Environental variables
- API_AI_CLIENT_ID (export API_AI_CLIENT_ID=b889d2db714c46e08b719319aec1039b - add to .bashrc if neccessary)


## Modules

### Perception
- Procrob_functional - ROS package from internet used for face recognition
- Cob_people_detection - A different ROS package from internet
- AWS face recognition - Custom ROS module uses AWS Rekognition
- Google SR - Custom ROS module for Google speech to text using python api

## Decision
- API.AI - Custom ROS module uses API.AI, can be imported from api-ai/ReceptionistNLP.zip provided in this repo
- Lex - Custom ROS module uses Lex, config for the Lex/Lambda AWS backend is provided in the receptionist-ever-aws folder, either to be manually created or via the command line/REST api

## Action
- Currently not implemented, plan is to write a custom ROS package to integrate with the Ever head via websockets or http

## Face training
- the current GUI face trainer is only for the procrob_functional module
- Run the procrob_functional/scripts/aws_saver.py script to update the AWS rekognition face database. Firstly you need to create a face collection called 'receptionist_collection'
- See documentation for cob_people_detection on how to update the face database for this module

## Adding additional modules
- The 2 main modules are receptionist_perception_system and decision_system
- All other modules interact with either of these main modules via a common ROS message (common interface)
- Simply write another ROS module to wrap your implementation and interact with the system using the common ROS messages (e.g. AWS_Lex)
- Or else modify an existing module to integrate with the system via the common ROS messages (e.g. Procrob_functional)

## Tensorflow speech-to-text-wavenet
- training data is removed due to size
- you can download from https://github.com/itzikgili/speech-to-text-wavenet and put into src/speech-to-text-wavenet/scripts/assets folder
- run train.py to train from data, this should generate files inside the train folder
- Does not work very well on actual data unfortunately, very very bad accuracy

## Help
- Please see slides for expected usage and rqt_graph images




# receptionist_uoa
# receptionist_uoa
