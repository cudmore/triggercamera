'''
20160229
treadmill

this is a master driver to run an experiment
this is NOT implemented to be a slave

if on Raspberry, turn on dio
	- dio to trigger a trial
	- dio on a new frame
	- dio to stop a trial
	
todo:
	include VideoServer.py
	not sure how to quickly trigger camera?
	if we are really master, then on startTrial we can just start the video
	- pass dio new frame to running pi camera
	
	- not sure if two python threads can share same dio pin (probably not)
	
	- maybe just make camera respond to dio start/stop/frame on its own set of three pins
		different from the start/stop/frame we are using here !!!
		
'''

import serial
import time
import os.path
from threading import Thread

import eventlet
eventlet.monkey_patch()

try:
	import picamera
except ImportError:
	print "\t=========================================================="
	print "\tWarning: treadmill.py did not find python library picamera"
	print '\t\tThis usually happens when code is not running on Raspberry Pi'
	print "\t=========================================================="
		
#
#eventually put this in a file
#serialStr = '/dev/tty.usbmodem618661' #teensy at work
#serialStr = '/dev/tty.usbmodem618661' #teensy?
#serialStr = '/dev/ttyUSB0' #hand soldered arduino micro (home debian)
serialStr = '/dev/tty.usbserial-A50285BI' # hand soldered at work
serialStr = '/dev/ttyACM0' #uno

options = {}
options['serial'] = {}
options['serial']['port'] = serialStr
options['serial']['baud'] = 115200 #57600
options['picamera'] = 0

trial = {}
trial['filePath'] = ''
trial['fileName'] = ''
trial['trialNumber'] = 0
trial['trialDur'] = 0 # (epochDur * numEpoch)

trial['epochNumber'] = 0
trial['epochDur'] = 5000
trial['numEpoch'] = 1

trial['preDur'] = 200
trial['postDur'] = 200
trial['numPulse'] = 5
trial['pulseDur'] = 100 #ms
trial['useMotor'] = 'motorOn' #{motorOn, motorLocked, motorFree}
trial['motorDel'] = 20 #ms
trial['motorDur'] = 50 #ms
trial['motorSpeed'] = 100

trial['trialDur'] = trial['numEpoch'] * trial['epochDur']

#end options
#
			
class treadmill():
	def __init__(self):
		self.animalID = 'default'
		self.trial = trial
				
		self.socketio = None
		
		try:
			self.ser = serial.Serial(options['serial']['port'], options['serial']['baud'], timeout=0.25)
		except:
			self.ser = None
			print "======================================================"
			print "ERROR: treadmill did not find serial port '", options['serial']['port'], "'"
			print "======================================================"
		
		if options['picamera']:
			print 'treadmill is using raspberry pi camera'
				
		#serial is blocking. we need our trial to run in a separate thread so we do not block user interface
		self.trialRunning = 0
		thread = Thread(target=self.background_thread, args=())
		thread.daemon  = True; #as a daemon the thread will stop when *this stops
		thread.start()
			
		#save all serial data to file, set in setsavepath
		self.savepath = ''
		self.filePtr = None
		
		self.arduinoStateList = None #grab from arduino at start of trial, write into each epoch file
		
		print 'treadmill.trial:', self.trial
		
	def background_thread(self):
		'''Background thread to continuously read serial. Used during a trial.'''
		while True:
			if self.trialRunning:
				str = self.ser.readline().rstrip()
				if len(str) > 0:
					print str
					self.NewSerialData(str)
			time.sleep(0.01)

	def bAttachSocket(self, socketio):
		print 'treadmill.bAttachSocket() attaching socketio:', socketio
		self.socketio = socketio

	def NewSerialData(self, str):
		'''
		we have received new serial data. pass it back to socketio
		special case is when we receive stopTrial
		'''
		#we want 'millis,event,val', if serial data does not match this then do nothing
		try:
			if len(str)>0 and self.socketio:
					#save to file
					if self.filePtr:
						self.filePtr.write(str + '\n')
					
					#print "\t=== treadmill.NewSerialData sending serial data to socketio: '" + str + "'"
					if self.socketio:
						self.socketio.emit('serialdata', {'data': str})
					
					#stop trial
					parts = str.split(',')
					if len(parts) > 1:
						if parts[1] == 'startEpoch':
							print '--->>> treadmill.NewSerialData() is starting epoch'
							self.startEpoch()
						if parts[1] == 'stopTrial':
							print '--->>> treadmill.NewSerialData() is stopping trial'
							self.stopTrial()
		except:
			print "=============="
			print "ERROR: treadmill.NewSerialData()"
			print "=============="

	def startTrial(self):
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0
			
		self.trial['trialNumber'] += 1
		self.trial['epochNumber'] = 0
		
		self.newepochfile(0)
		
		if self.socketio:
			self.socketio.emit('serialdata', {'data': "=== Trial " + str(self.trial['trialNumber']) + " ==="})
		
		self.ser.write('startTrial\n')
		self.trialRunning = 1

		print 'treadmill.startTrial()'
		
		return 1
		
	def startEpoch(self):
		if not self.trialRunning:
			print 'warning: startEpoch() trial is not running'
			return 0
			
		self.trial['epochNumber'] += 1
				
		self.newepochfile(self.trial['epochNumber'])

		if self.socketio:
			self.socketio.emit('serialdata', {'data': "=== Epoch " + str(self.trial['epochNumber']) + " ==="})
		
		#self.ser.write('startTrial\n')
		#self.trialRunning = 1

		#print 'treadmill.startTrial()'
		
		return 1
		
	def stopTrial(self):
		if self.filePtr:
			self.filePtr.close()
			self.filePtr = None
			
		self.trialRunning = 0

		self.ser.write('stopTrial\n')
		if self.socketio:
			self.socketio.emit('serialdata', {'data': "=== Stop Trial " + str(self.trial['trialNumber']) + " ==="})

		print 'treadmill.stopTrial()'
		
	def newepochfile(self, epochNumber):
		# open a file for this trial
		dateStr = time.strftime("%Y%m%d")
		timeStr = time.strftime("%H%M%S")
		datetimeStr = dateStr + '_' + timeStr

		sessionStr = ''
		sessionFolder = ''
		if self.animalID and not (self.animalID == 'default'):
			sessionStr = self.animalID + '_'
			sessionFolder = dateStr + '_' + self.animalID
		
		thisSavePath = self.savepath + dateStr + '/'
		if not os.path.exists(thisSavePath):
			os.makedirs(thisSavePath)
		thisSavePath += sessionFolder + '/'
		if not os.path.exists(thisSavePath):
			os.makedirs(thisSavePath)
		
		trialFileName = sessionStr + datetimeStr + '_t' + str(self.trial['trialNumber']) + '_e' + str(self.trial['epochNumber']) + '.txt'
		trialFilePath = thisSavePath + trialFileName
		
		self.trial['filePath'] = trialFilePath
		self.trial['fileName'] = trialFileName
		
		#
		#header line 1 is all arduino parameters
		if epochNumber==0:
			self.arduinoStateList = self.GetArduinoState()		

		self.filePtr = open(trialFilePath, 'w')

		self.filePtr.write('trial='+str(self.trial['trialNumber'])+';')
		self.filePtr.write('epoch='+str(self.trial['epochNumber'])+';')
		self.filePtr.write('date='+dateStr+';')
		self.filePtr.write('time='+timeStr+';')
		
		for state in self.arduinoStateList:
			self.filePtr.write(state + ';')
			
		self.filePtr.write('\n')
		
		#
		#header line 2 is column names
		self.NewSerialData('millis,event,value')

		#
		#each call to self.NewSerialData() will write serial data to this file
		
	def settrial(self, key, val):
		'''
		set value for *this
		send serial to set value on arduino
		'''
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0

		print "=== treadmill.settrial() key:'" + key + "' val:'" + val + "'"
		if key in self.trial:
			self.trial[key] = val
			serialCommand = 'settrial,' + key + ',' + val 
			serialCommand = str(serialCommand)
			print "\ttreadmill.settrial() writing to serial '" + serialCommand + "'"
			self.ser.write(serialCommand + '\n')
		else:
			print '\tERROR: treadmill:settrial() did not find', key, 'in trial dict'

	def updatetrial(self):
		numEpoch = long(self.trial['numEpoch'])
		epochDur = long(self.trial['epochDur'])
		totalDur = numEpoch * epochDur
		print 'updatetrial() set trialDur=', totalDur
		self.trial['trialDur'] = str(totalDur)
		
	def GetArduinoState(self):
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0

		if self.socketio:
			self.socketio.emit('serialdata', {'data': "=== Arduino State ==="})
		self.ser.write('getState\n')
		#time.sleep(.02)
		stateList = self.emptySerial()
		if self.socketio:
			self.socketio.emit('serialdata', {'data': "=== Done ==="})
		return stateList
		
	def emptySerial(self):
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0

		theRet = []
		line = self.ser.readline()
		i = 0
		while line:
			line = line.rstrip()
			theRet.append(line)
			self.NewSerialData(line)
			line = self.ser.readline()
			i += 1
		return theRet
		
	def setserialport(self, newPort):
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0

		if os.path.exists(newPort) :
			print 'setserialport() port', newPort, 'exists'
			options['serial']['port'] = newPort
			return 1
		else:
			print 'setserialport() port', newPort, 'does not exist'
			return 0
			
	def checkserialport(self):
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0

		port = options['serial']['port']
		print 'checking', port
		if os.path.exists(port) :
			print 'exists'
			return 1, port
		else:
			print 'does not exist'
			return 0, port
			
	def checkarduinoversion(self):
		if self.trialRunning:
			print 'warning: trial is already running'
			return 0

		self.ser.write('version\n')
		self.emptySerial()
		
	def setsavepath(self, str):
		self.savepath = str
		