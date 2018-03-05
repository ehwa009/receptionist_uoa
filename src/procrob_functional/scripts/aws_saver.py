#!/usr/bin/python
import os
import boto3
from os import environ
from PIL import Image
import io

file = open(os.path.dirname(__file__) + '/../train.txt')

client = boto3.client('rekognition')

for line in file.readlines():
	imgPath = "/../" + line.split()[2]
	image = Image.open(os.path.dirname(__file__) + imgPath)
	imgByteArr = io.BytesIO()
	image.save(imgByteArr, format='PNG')
	imgByteArr = imgByteArr.getvalue() 

	response = client.index_faces(Image={'Bytes': imgByteArr}, CollectionId="receptionist_collection",
		ExternalImageId=line.split()[1], DetectionAttributes=["ALL"])
	print(response)

