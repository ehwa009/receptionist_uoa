#!/usr/bin/python

from Tkinter import *
from ttk import Notebook
import sys
import subprocess
import signal
from threading import Thread
import os
import re

root = Tk()
root.title("Receptionist GUI")

def launchOpenni():
	print("launching openni...")
	sys.stdout.flush()
	global openniProcess
	openniProcess = subprocess.Popen("roslaunch openni_launch openni.launch", shell=True)
	text.configure(state='normal')
	text.insert('end', 'Some Text')
	text.configure(state='disabled')

#
# added by Eddie.
# This is for temperary camera usage.
#
def launchUSBcam():
	print("launching USB cammera...")
	sys.stdout.flush()
	global USBcamProcess
	USBcamProcess = subprocess.Popen("roslaunch usb_cam usb_cam.launch", shell=True)
	text.configure(state='normal')
	text.insert('end', 'USB cam has been launched.\n')
	text.configure(state='disabled')
	
def launchReceptionist():
	print("launching perception system...")
	global receptionistProcess
	args = ["roslaunch", "receptionist_perception_system", "perception.launch"]
	args.append("procrob:=true") if procrobCheckVar.get() == 1 else args.append("procrob:=false")
	args.append("cob:=true") if cobCheckVar.get() == 1 else args.append("cob:=false")
	args.append("aws:=true") if awsCheckVar.get() == 1 else args.append("aws:=false")
	args.append("speech:=true") if googleSRCheckVar.get() + witSRCheckVar.get() + houndifySRCheckVar.get() + bingSRCheckVar.get() > 0 else args.append("speech:=false")
	args.append("google_speech:=true") if googleSRCheckVar.get() == 1 else args.append("google_speech:=false")
	args.append("wit_speech:=true") if witSRCheckVar.get() == 1 else args.append("wit_speech:=false")
	args.append("houndify_speech:=true") if houndifySRCheckVar.get() == 1 else args.append("houndify_speech:=false")
	args.append("bing_speech:=true") if bingSRCheckVar.get() == 1 else args.append("bing_speech:=false")
	args.append("pocketsphinx_speech:=true") if pocketsphinxSRCheckVar.get() == 1 else args.append("pocketsphinx_speech:=false")

	receptionistProcess = subprocess.Popen(args, stdout=subprocess.PIPE, bufsize=1)
	sys.stdout.flush()
	t = Thread(target=display_output)
	t.daemon = True # thread dies with the program
	t.start()

def launchDecision():
	print("launching decision system...")
	global decisionSystemProcess
	args = ["roslaunch", "decision_system", "decision.launch"]
	args.append("api_ai:=true") if apiAiCheckVar.get() == 1 else args.append("api_ai:=false")
	args.append("lex:=true") if lexCheckVar.get() == 1 else args.append("lex:=false")
	args.append("google_tts:=true") if googleTTSCheckVar.get() == 1 else args.append("google_tts:=false")
	args.append("python_tts:=true") if pythonTTSCheckVar.get() == 1 else args.append("python_tts:=false")
	args.append("aws_polly_tts:=true") if awsPollyTTSCheckVar.get() == 1 else args.append("aws_polly_tts:=false")

	decisionSystemProcess = subprocess.Popen(args, stdout=subprocess.PIPE, bufsize=1)
	sys.stdout.flush()
	t = Thread(target=display_output)
	t.daemon = True # thread dies with the program
	t.start()

def quitReceptionist():
	print("quitting perception system...")
	receptionistProcess.send_signal(signal.SIGINT) #You may also use .terminate() method
	receptionistProcess.terminate()
	subprocess.Popen("rosnode list | grep -ie Receptionist | awk '{print $1}' | xargs -r rosnode kill", shell=True)
	subprocess.Popen("rosnode list | grep -ie Procrob | awk '{print $1}' | xargs -r rosnode kill", shell=True)
	subprocess.Popen("rosnode list | grep -ie Speech | awk '{print $1}' | xargs -r rosnode kill", shell=True)
	subprocess.Popen("rosnode list | grep -ie Face | awk '{print $1}' | xargs -r rosnode kill", shell=True)

def quitDecision():
	print("quitting decision system...")
	decisionSystemProcess.send_signal(signal.SIGINT) #You may also use .terminate() method
	decisionSystemProcess.terminate()
	subprocess.Popen("rosnode list | grep -ie Decision | awk '{print $1}' | xargs -r rosnode kill", shell=True)
	subprocess.Popen("rosnode list | grep -ie ApiAi | awk '{print $1}' | xargs -r rosnode kill", shell=True)
	subprocess.Popen("rosnode list | grep -ie AwsLex | awk '{print $1}' | xargs -r rosnode kill", shell=True)

def faceTrain():
	# change to use face_trainer as adapter
	print("rostopic pub -1 /Procrob/fr_order face_recognition/FRClientGoal -- 2 \"" + faceLabelText.get() + "\"")
	subprocess.Popen("rostopic pub -1 /Procrob/fr_order face_recognition/FRClientGoal -- 2 \"" 
		+ faceLabelText.get() + "\"", shell=True)
	sys.stdout.flush()

def faceRefresh():
	print("rostopic pub -1 /Procrob/fr_order face_recognition/FRClientGoal -- 3")
	subprocess.Popen("rostopic pub -1 /Procrob/fr_order face_recognition/FRClientGoal -- 3", shell=True)
	#subprocess.Popen("rm procrob_functional/facedata.xml", shell=True)
	sys.stdout.flush()


# This method takes keyboard input then, hand the input over to the nlp node
def mockSpeechInput(event=None):
	text = inputText.get()
	# with open("/home/wyep266/transcripts.txt", "a") as myfile:
	# 	myfile.write(text.upper() + "\n")
	print("rostopic pub -1 /receptionist_perception_output std_msgs/String \"!!str " + text + "\"")
	subprocess.Popen("rostopic pub -1 /receptionist_perception_output std_msgs/String \"!!str " + text + "\"", shell=True) 
	inputText.set("")


tabs = Notebook(root)
tabs.pack(fill=BOTH, expand=True)
tabs.pressed_index = None
frame = Frame(tabs)
faceTrainFrame = Frame(tabs)

root.bind('<Return>', mockSpeechInput)

# main frame
var = StringVar()
Label( frame, textvariable=var, height=2, fg="blue", font=("Arial 12 bold") ).grid(row=0, sticky=W)
var.set("Receptionist Ever")

var2 = StringVar()
Label( frame, textvariable=var2, font="Arial 10 bold" ).grid(row=1, sticky=W)
var2.set("Face Recogntion")

procrobCheckVar = IntVar()
cobCheckVar = IntVar()
awsCheckVar = IntVar()
Checkbutton(frame, text = "Procrob Functional", variable = procrobCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=2, column=0, sticky=W)
# Checkbutton(frame, text = "Cob People Detection", variable = cobCheckVar, onvalue = 1, offvalue = 0, width = 25).grid(row=2, column=1, sticky=W)
Checkbutton(frame, text = "AWS", variable = awsCheckVar, onvalue = 1, offvalue = 0, width = 25).grid(row=2, column=1, sticky=W)

var2 = StringVar()
Label( frame, textvariable=var2, font="Arial 10 bold" ).grid(row=4, sticky=W)
var2.set("Speech Recogntion")

googleSRCheckVar = IntVar()
googleSRCheckVar.set(1)
witSRCheckVar = IntVar()
houndifySRCheckVar = IntVar()
bingSRCheckVar = IntVar()
pocketsphinxSRCheckVar = IntVar()
Checkbutton(frame, text = "Google SR", variable = googleSRCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=5, column=0, sticky=W)
Checkbutton(frame, text = "Wit.AI SR", variable = witSRCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=5, column=1, sticky=W)
Checkbutton(frame, text = "Houndify SR", variable = houndifySRCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=5, column=2, sticky=W)
Checkbutton(frame, text = "Bing SR", variable =bingSRCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=5, column=3, sticky=W)
Checkbutton(frame, text = "PocketSphinx SR(working..)", variable =pocketsphinxSRCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=5, column=4, sticky=W)

var3 = StringVar()
Label( frame, textvariable=var3, font="Arial 10 bold" ).grid(row=6, sticky=W)
var3.set("AI Decision System")

apiAiCheckVar = IntVar()
lexCheckVar = IntVar()
lexCheckVar.set(1)
Checkbutton(frame, text = "API.AI", variable = apiAiCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=7, column=0, sticky=W)
Checkbutton(frame, text = "Lex", variable = lexCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=7, column=1, sticky=W)

var4 = StringVar()
Label( frame, textvariable=var4, font="Arial 10 bold" ).grid(row=8, sticky=W)
var4.set("Text to Speech Generator")

googleTTSCheckVar = IntVar()
pythonTTSCheckVar = IntVar()
awsPollyTTSCheckVar = IntVar()
awsPollyTTSCheckVar.set(1)
Checkbutton(frame, text = "Google TTS", variable = googleTTSCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=9, column=0, sticky=W)
Checkbutton(frame, text = "Python/Linux native", variable = pythonTTSCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=9, column=1, sticky=W)
Checkbutton(frame, text = "AWS Polly", variable = awsPollyTTSCheckVar, onvalue = 1, offvalue = 0, width = 20).grid(row=9, column=2, sticky=W)

Button(frame, text ="Launch OpenNI", command = launchOpenni).grid(row=10, column=0)
Button(frame, text ="USBCam", command = launchUSBcam).grid(row=10, column=1)
Button(frame, text ="Launch Perception", command = launchReceptionist).grid(row=11, column=0)
Button(frame, text ="Quit Perception", command = quitReceptionist).grid(row=11, column=1)

Button(frame, text ="Launch Decision", command = launchDecision).grid(row=12, column=0)
Button(frame, text ="Quit Decision", command = quitDecision).grid(row=12, column=1)

text = Text(frame, width=40, height=10, font=("Helvetica",32))

text.configure(state='disabled')
text.grid(row=13, columnspan=5)

textStringVar = StringVar()
Label(frame, textvariable=textStringVar, font="Arial 10" ).grid(row=14, column=0)
textStringVar.set("Enter text to send: ")
inputText = StringVar()
Entry(frame, textvariable=inputText, width = 35).grid(row=14, column=1, columnspan=3)
Button(frame, text ="Send", command = mockSpeechInput).grid(row=14, column=3)


# Face train frame
var4 = StringVar()
Label( faceTrainFrame, textvariable=var4, font="Arial 10" ).grid(row=0, column=0)
var4.set("Enter name: (no spaces)")

faceLabelText = StringVar()
Entry(faceTrainFrame, textvariable=faceLabelText).grid(row=0, column=1)
Button(faceTrainFrame, text ="Train Procrob", command = faceTrain).grid(row=0, column=2)
Button(faceTrainFrame, text ="Refresh", command = faceRefresh).grid(row=0, column=3)

# add tabs to notebook, add notebook to root
tabs.add(frame, text='Perception')
tabs.add(faceTrainFrame, text='Face Train')
tabs.grid(row=1)




# print output to console

def display_output():
	# try:
	# 	for line in iter(receptionistProcess.stdout.readline, ""):
	# 		text.configure(state='normal')
	# 		text.insert('end', "perception: " + line)
	# 		text.configure(state='disabled')
	# 		text.see("end")
	# except NameError:
	# 	print("")

	try:
		for line in iter(decisionSystemProcess.stdout.readline, ""):
			m = re.search('^(.* you said:(.*)|.* receptionist says:(.*))$', line)
			if m:
				text.configure(state='normal')
				if m.group(2):
					text.insert('end', m.group(2) + "\n")
				if m.group(3):
					text.insert('end', m.group(3) + "\n")
				text.configure(state='disabled')
				text.see("end")
	except NameError:
		print("")

root.mainloop()