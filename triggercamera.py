#Author: Robert H Cudmore
#Web: http://robertcudmore.org
#Date: 20151205
#Purpose: A rewrite of VideoThread.py
#
#This should not use pins but respond to function calls instead

'''
Usage
==========
import triggercamera
v=triggercamera.TriggerCamera()

v.startArm() #arm camera to respond to triggers

v.stopArm() #turn off triggering

#start and stop video recording as much as you like
v.startVideo()
v.stopVideo()

v.doTimelapse=1
v.doTimelapse=0

v.stopArm()
'''

#todo: watch a folder and (based on option), put last/new file in save .txt header
#todo: add in serial communication with an arduino
#todo: add option to arm on startup (add to config.ini)

import os, time, io, math, threading
import numpy as np
from datetime import datetime #to get fractional seconds
import picamera
import RPi.GPIO as GPIO
import ConfigParser # to load config.ini
import serial
import subprocess
#import ftplib #to send recorded video to server

class TriggerCamera(threading.Thread):
	def __init__(self):
		print '\n\nTriggerCamera() constructor'
		threading.Thread.__init__(self)

		#when this script is running, it will always be armed
		self.isArmed = 0
		self.streamIsRunning = 0
		self.videoStarted = 0

		self.stream = None

		self.trialNumber = 0
		self.trialStartTime = 0
		self.savepath = '/home/pi/video/' + time.strftime('%Y%m%d') + '/'
		if not os.path.exists(self.savepath):
			print '\tVideoServer is making output directory:', self.savepath
			os.makedirs(self.savepath)
		
		self.savename = '' # the prefix to save all files
		
		self.logFileName = None
		self.logFilePath = ''
 
		self.beforefilename = ''
		self.afterfilename = ''
		
		self.beforefilepath = ''
		self.afterfilepath = ''
		
		self.startTime = 0 #when we start recording in run(), triggered by startVideo()
		self.recordDuration = float('inf') #10 #seconds, set to infinity to then stop with stopVideo()
		
		self.doTimelapse = 0
		self.stillinterval = 5 #second
		self.lastimage = ''
		
		self.serial = None #serial.Serial('/dev/ttyACM0')  # open serial port
	
		#keep track of remaining/size of video drive
		self.gbSize = ''
		self.gbRemaining = ''
		self.drivespaceremaining()
		
		#keep track of CPU temperature
		self.cpuTemperature = ''
		
		#set up local parameter
		self.config = {}
		self.config['camera'] = {}
		self.config['camera']['fps'] = 30
		self.config['camera']['resolution'] = (640, 480)
		self.config['camera']['bufferSeconds'] = 5
		
		self.config['triggers'] = {}
		self.config['triggers']['useTwoTriggerPins'] = True
		self.config['triggers']['triggerpin'] = 27
		self.config['triggers']['framepin'] = 17

		self.config['ledpin1'] = 9
		self.config['ledpin2'] = 10

		self.config['simulatescope'] = {}
		self.config['simulatescope']['on'] = 0
		
		#fill in parameters from config.ini
		self.ParseConfigFile()
		
		triggerpin = self.config['triggers']['triggerpin']
		framepin = self.config['triggers']['framepin']

		GPIO.setmode(GPIO.BCM)	 # set up BCM GPIO numbering  

		self.led1On = 0
		self.led2On = 0
		GPIO.setup(self.config['ledpin1'], GPIO.OUT)	#
		GPIO.setup(self.config['ledpin2'], GPIO.OUT)	#

		GPIO.setup(self.config['triggers']['triggerpin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#
		GPIO.setup(self.config['triggers']['framepin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#

		if self.config['triggers']['useTwoTriggerPins']:
			print '\ttwo pin style triggerpin is', triggerpin
			print '\ttwo pin style framepin is', framepin
			GPIO.add_event_detect(triggerpin, GPIO.BOTH, callback=self.triggerPinCallback) #, bouncetime=10)
			GPIO.add_event_detect(framepin, GPIO.RISING, callback=self.framePinCallback) #, bouncetime=10)
		else:
			print 'scanimage style triggerpin is', triggerpin
			GPIO.add_event_detect(triggerpin, GPIO.BOTH, callback=self.scanimageCallback) #, bouncetime=10)
			
		self.lastFrameTime = 0 # set in newFrame() and checked in main run loop for stop condition
		self.lastFrameTimeout = 1 # seconds
		
		self.numFrames = 0
		self.ardFrames = 0
		
		#keep a list of frame,time
		self.frameList = []

		#print '\ttrigger camera constructor initializing camera'
		#self.camera = picamera.PiCamera()
		#self.camera.resolution = (self.config['camera']['resolution'][0], self.config['camera']['resolution'][1])
		#self.camera.led = 0
		#self.camera.framerate = self.config['camera']['fps']
		#self.camera.start_preview()

		self.daemon = True
		print '\ttriggercamera constructor is calling start()'
		self.start()
		
	def sendSerial(self, str):
		serialPort = self.config['serialPort']
		print 'triggerCamera::sendSerial()', 'serialPort=', serialPort
		try:
			#self.serial = serial.Serial(serialPort, baudrate=115200)
			self.serial = serial.Serial(serialPort, baudrate=9600)
			print('\topened port' + self.serial.name)
			self.serial.write(str)
			self.serial.close()
		except:
			print 'ERROR: triggercamera:sendSerial()'
			
	'''
	one callback for complex scanimage frame clock
	this is a really bad solution that just assumes ANY change on pin
	problem is when pulse is really fast, down on frame then reading for down will miss it and read an up
	'''
	def scanimageCallback(self, pin):
		pinIsUp = GPIO.input(pin)
		if pinIsUp and not self.videoStarted:
			 self.startVideo()
		elif not pinIsUp and self.videoStarted:
			timeSeconds = time.time()
			self.newFrame(timeSeconds)
			 
	'''
	two callbacks for two pin configuration (i) trigger and (ii) frame
	'''
	def triggerPinCallback(self, pin):
		#timeSeconds = time.time()
		pinIsUp = GPIO.input(pin)
		if pinIsUp and not self.videoStarted:
			self.startVideo()
		elif not pinIsUp and self.videoStarted:
			self.stopVideo()
			
	def framePinCallback(self, pin):
		timeSeconds = time.time()
		if self.videoStarted:
			self.newFrame(timeSeconds)
			
	def ParseConfigFile(self):
		if self.isArmed == 1:
			print 'Warning: ParseConfigFile() not alowed while isArmed'
			return
			
		print '\ttriggercamera.ParseConfigFile() is reading config file from config.ini'

		Config = ConfigParser.ConfigParser()
		Config.read('config.ini')
		Config.sections()
		
		self.config['camera']['fps'] = int(Config.get('camera','fps'))
		
		resolution = Config.get('camera','resolution').split(',')
		self.config['camera']['resolution'] = (int(resolution[0]), int(resolution[1]))		
		self.config['camera']['bufferSeconds'] = int(Config.get('camera','bufferSeconds'))		
		
		self.config['triggers']['useTwoTriggerPins'] = int(Config.get('triggers','useTwoTriggerPins'))
		self.config['triggers']['triggerpin'] = int(Config.get('triggers','triggerpin'))
		self.config['triggers']['framepin'] = int(Config.get('triggers','framepin'))

		self.config['ledpin1'] = int(Config.get('led','ledpin1'))
		self.config['ledpin2'] = int(Config.get('led','ledpin2'))

		self.config['serialPort'] = Config.get('system', 'serialPort')

		print '\tdone reading config file'
			
	'''
	def sendtoserver(self):
		try:
			ip = '192.168.1.200'
			ftpDir = 'securitycam/pi40'
			ftp = ftplib.FTP(ip)
			ftp.login("cudmore", "poetry7d")
			ftp.cwd(ftpDir)
			print 'login to', ip, 'ok. cwd', ftpDir
			ftp.storbinary("STOR " + self.beforefilename, open(self.beforefilepath, "rb"))
			print '\tsent', self.beforefilename
			ftp.storbinary("STOR " + self.afterfilename, open(self.afterfilepath, "rb"))
			print '\tsent', self.afterfilename
		except:
			print '\t-->> exception in sendtoserver'
	'''
			
	def startArm(self):
		print '\tVideoThread startArm()'
		if self.streamIsRunning:
			print 'ERROR: Can not start arm while stream is running'
			return 0
			
		if self.isArmed == 0:
			try:
				print '\ttriggercamera::startArm()   initializing camera'
				self.camera = picamera.PiCamera()
				self.camera.resolution = (self.config['camera']['resolution'][0], self.config['camera']['resolution'][1])
				self.camera.led = 0
				self.camera.framerate = self.config['camera']['fps']
				self.camera.start_preview()

				print '\ttriggercamera::startArm() starting circular stream'
				self.stream = picamera.PiCameraCircularIO(self.camera, seconds=self.config['camera']['bufferSeconds'])
				self.camera.start_recording(self.stream, format='h264')

				self.isArmed = 1 #order is important, must come after we instantiate camera
		
			#except PiCameraMMALError:
			#	print 'startArm() error: PiCameraMMALError'
			except:
				print 'ERROR: startArm() error'
				
	def stopArm(self):
		print '\tVideoThread stopArm()'
		if self.isArmed == 1:
			self.isArmed = 0
			self.camera.stop_recording()	
			
			self.camera.close()
			
			print '\tVideoServer stopArm() is done'

	def startVideoStream(self):
		print 'triggercamera::startVideoStream()'
		if self.isArmed:
			print "ERROR: Can not start stream while armed"
		elif not self.streamIsRunning:
			cmd = '/home/pi/Sites/triggercamera/stream_start.sh'
			subprocess.Popen(cmd, shell=True, executable='/bin/bash')
			self.streamIsRunning = 1
		
	def stopVideoStream(self):
		#subprocess.check_output(['ls', '-l'])
		print 'triggercamera::stopVideoStream()'
		if self.streamIsRunning:
			cmd = '/home/pi/Sites/triggercamera/stream_stop.sh'
			subprocess.Popen(cmd, shell=True, executable='/bin/bash')
			self.streamIsRunning = 0
		
	def startVideo(self):
		'''
		todo: add parameter for recordDuration
		'''
		timeSeconds = time.time()
		if self.isArmed and not self.videoStarted:
			self.savename = self.GetTimestamp()
			self.trialNumber += 1
			self.trialStartTime = timeSeconds
			self.numFrames = 0
			self.videoStarted = 1
			if self.camera:
				self.camera.annotate_text = 'S'
				self.camera.annotate_background = picamera.Color('black')
			
			self.logFileName = self.savename + '_t' + str(self.trialNumber) + '.txt'
			self.logFilePath = self.savepath + self.logFileName
			
			self.frameList = []
			self.newOutputLine(timeSeconds, 'startVideo', None)
			print timeSeconds, 'bExperiment::startVideo()'

	def stopVideo(self):
		timeSeconds = time.time()
		if self.isArmed and self.videoStarted:
			self.videoStarted = 0
			#if self.camera:
			#	self.camera.annotate_text = ''
			#	self.camera.annotate_background = None

			self.newOutputLine(timeSeconds, 'stopVideo', None)
			self.saveOutputFile()
			
			self.saveArduinoOutput()

			self.drivespaceremaining() #calculate drive space remaining
			#print timeSeconds, 'bExperiment::stopVideo()'
			
	def saveArduinoOutput(self):
		'''
		see: http://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package
		'''
		
		print '*** triggerCamera::saveArduinoOutput() is reading from serial'
		serialPort = self.config['serialPort']
		outFile = []
		try:
			#ser = serial.Serial(serialPort, baudrate=115200) #, timeout=0.5)
			ser = serial.Serial(serialPort, baudrate=9600) #, timeout=0.5)
			ser.writeTimeout = 2
			ser.timeout = 1

			ser.flushInput()
			ser.flushOutput()
			
			ser.write(b'trial')	
			
			time.sleep(0.5)
			
			serialIn = []
			while True:
				response = ser.readline()
				#print 'response=', response
				if response:
					serialIn.append(response.rstrip())
				else:
					break
		
			ser.close()

		except:
			print '\tERROR: triggerCamera::saveArduinoOutput()'
			
		print '*** triggerCamera::saveArduinoOutput() is appending to file:', self.logFilePath
		dummyStr = ',,'
		self.ardFrames = 0
		with open(self.logFilePath, 'a') as textfile:
			for item in serialIn:
				textfile.write("%s%s\n" % (dummyStr, item))
				if item.find('ardFrame') >= 0:
					self.ardFrames += 1
		self.ardFrames -= 2 # 2 lines are start/stop
		print '*** triggerCamera::saveArduinoOutput() done.', 'arduino frames = ', self.ardFrames
		
	def newOutputLine(self, timeSeconds, eventName, frameNumber):
		localtime = time.localtime(timeSeconds)
		dateStr = time.strftime('%Y%m%d',localtime)
		timeStr = time.strftime('%H%M%S', localtime) #expand this to have fraction
		listLine = dateStr + ',' + timeStr + ',' + str(timeSeconds) + ',' + eventName + ','
		if frameNumber is not None:
			listLine += str(frameNumber)
		self.frameList.append(listLine)
	
	#date,time,seconds,event,frameNumber
	def saveOutputFile(self):
		print 'triggercamera.saveOutputFile() is writing log file:', self.logFilePath
		localtime = time.localtime(time.time())
		with open(self.logFilePath, 'a') as textfile:
			#header line
			dateStr = time.strftime('%Y%m%d',localtime)
			timeStr = time.strftime('%H%M%S', localtime) #expand this to have fraction
			headerStr = 'date=' + dateStr + ','
			headerStr += 'time=' + timeStr + ','
			headerStr += 'trial=' + str(self.trialNumber) + ','
			headerStr += 'fps=' + str(self.config['camera']['fps']) + ','
			headerStr += 'width=' + str(self.config['camera']['resolution'][0]) + ','
			headerStr += 'height=' + str(self.config['camera']['resolution'][1]) + ','
			headerStr += 'numFrames=' + str(self.numFrames) + ','
			headerStr += 'ardFrames=' + str(self.ardFrames)
			#headerStr += 'filename=' + self.logFilePath 
			#column names
			textfile.write(headerStr + '\n')
			textfile.write("date,time,seconds,event,frameNumber\n")
		#data
		with open(self.logFilePath, 'a') as textfile:
			for item in self.frameList:
				textfile.write("%s\n" % item)
	
	def newFrame(self, timeSeconds):
		self.lastFrameTime = timeSeconds
		self.numFrames += 1
		self.camera.annotate_text = str(self.lastFrameTime) + ' ' + str(self.numFrames)
		
		self.newOutputLine(timeSeconds, 'numFrames', self.numFrames)
		
		#if np.mod(self.numFrames,10) == 0:
		#	print timeSeconds, 'numFrames is', self.numFrames
		  
	def GetTimestamp(self):
		#returns integer seconds (for file names)
		return time.strftime('%Y%m%d') + '_' + time.strftime('%H%M%S')
	
	def GetTimestamp2(self):
		# returns fraction seconds (for log file entries)
		#datetime.datetime.now().strftime("%H:%M:%S.%f")
		return time.strftime('%Y%m%d') + '_' + datetime.now().strftime("%H%M%S.%f")

	#called from run()
	def write_video(self, stream, beforeFilePath):
		# Write the entire content of the circular buffer to disk. No need to
		# lock the stream here as we're definitely not writing to it
		# simultaneously
		#with io.open(self.savepath + 'before.h264', 'wb') as output:
		with io.open(beforeFilePath, 'wb') as output:
			for frame in stream.frames:
				if frame.frame_type == picamera.PiVideoFrameType.sps_header:
					stream.seek(frame.position)
					break
			while True:
				buf = stream.read1()
				if not buf:
					break
				output.write(buf)
		# Wipe the circular stream once we're done
		stream.seek(0)
		stream.truncate()

	#start arm
	def run(self):
		print '\tVideoServer run() is initializing [can only call this once]' 
		lasttime = time.time()
		
		#self.startArm()
		
		useTwoTriggerPins = self.config['triggers']['useTwoTriggerPins']
		
		while True:
			if self.isArmed:
				while (self.isArmed):
					try:
						#self.camera.wait_recording(0.005)
						if self.videoStarted:
							self.startTime = time.time() #seconds, linux epoch
							self.beforefilename = self.savename + '_before' + '.h264'
							self.afterfilename = self.savename + '_after' + '.h264'
							self.beforefilepath = self.savepath + self.beforefilename
							self.afterfilepath = self.savepath + self.afterfilename
							# record the frames "after" motion
							self.camera.split_recording(self.afterfilepath)
							# Write the 10 seconds "before" motion to disk as well
							self.write_video(self.stream, self.beforefilepath)
				
							stopOnTrigger = 0
							while not stopOnTrigger and self.videoStarted and (time.time()<(self.startTime + self.recordDuration)):
								self.camera.wait_recording(1) # seconds
								#print 'wait_recording() finished'
								#this is for single trigger/frame pin in ScanImage
								if not useTwoTriggerPins and (time.time() > (self.lastFrameTime + self.lastFrameTimeout)):
									print 'run() is stopping after last frame timeout'
									stopOnTrigger = 1
								
							print '\ttriggercamera::run() received stopOnTrigger OR self.videoStarted==0 OR past recordDuration'
							self.camera.split_recording(self.stream)
							self.stopVideo() #
							#self.saveArduinoOutput()
							#self.sendtoserver()
						
						#capture a foo.jpg frame every stillInterval seconds
						thistime = time.time()
						if self.doTimelapse and thistime > (lasttime+self.stillinterval):
							lasttime = thistime
							self.lastimage = self.GetTimestamp2() + '.jpg'
							print 'capturing still frame:', self.lastimage
							self.camera.capture(self.savepath + self.lastimage, use_video_port=True)
			
						time.sleep(0.005) # seconds
					except:
						print '\tVideoServer except clause -->>ERROR'
				print '\tVideoServer.run() fell out of while(self.isArmed) loop'
			time.sleep(0.05)
		print '\tVideoServer.run() terminating [is never called]'
		
		#i should wrap this in a try: except: finally:
		if self.camera:
			self.camera.close()
		GPIO.cleanup()
		
	def drivespaceremaining(self):
		#see: http://stackoverflow.com/questions/51658/cross-platform-space-remaining-on-volume-using-python
		statvfs = os.statvfs('/home/pi/video')
		
		#http://www.stealthcopter.com/blog/2009/09/python-diskspace/
		capacity = statvfs.f_bsize * statvfs.f_blocks
		available = statvfs.f_bsize * statvfs.f_bavail
		used = statvfs.f_bsize * (statvfs.f_blocks - statvfs.f_bavail) 
		#print used/1.073741824e9, available/1.073741824e9, capacity/1.073741824e9
		print 'drivespaceremaining()', used/1.073741824e9, available/1.073741824e9, capacity/1.073741824e9
		self.gbRemaining = available/1.073741824e9
		self.gbSize = capacity/1.073741824e9

		#round to 2 decimal places
		self.gbRemaining = "{0:.2f}".format(self.gbRemaining)
		self.gbSize = "{0:.2f}".format(self.gbSize)
		
		#self.gbRemaining = statvfs.f_bavail * statvfs.f_frsize / 1024 / 1024 / 1000 #GB available
		#self.gbSize = statvfs.f_blocks * statvfs.f_frsize / 1024 / 1024 / 1000 #GB size
		print self.gbRemaining, self.gbSize

		#cpu temperature
		res = os.popen('vcgencmd measure_temp').readline()
		self.cpuTemperature = res.replace("temp=","").replace("'C\n","")
		print 'cpu temp = ', self.cpuTemperature
		
		