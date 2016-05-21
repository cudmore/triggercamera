#Author: Robert H Cudmore
#Web: http://robertcudmore.org
#Date: 20151205
#Purpose: A rewrite of VideoThread.py
#
#This should not use pins but respond to function calls instead

'''
Usage
==========
import VideoServer
v=VideoServer.VideoServer()

#start video server daemon
v.daemon = True
v.start()

v.startArm()

#start and stop video recording as much as you like
v.startVideo()
v.stopVideo()

v.startVideo()
v.stopVideo()

v.doTimelapse=1
v.doTimelapse=0

v.stopArm()
'''
import os, time, io, math, threading
from datetime import datetime #to get fractional seconds
import picamera
import RPi.GPIO as GPIO
import ConfigParser # to load config.ini
import ftplib #to send recorded video to server

class TriggerCamera(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        #when this script is running, it will always be armed
        self.isArmed = 0
        self.videoStarted = 0

        self.stream = None

        self.savepath = '/home/pi/video/' + time.strftime('%Y%m%d') + '/'
        if not os.path.exists(self.savepath):
            print '\tVideoServer is making output directory:', self.savepath
            os.makedirs(self.savepath)
        
        self.savename = '' # the prefix to save all files
        
        self.logFileName = None
        self.logFilePath = None
 
        self.beforefilename = ''
        self.afterfilename = ''
        
        self.beforefilepath = ''
        self.afterfilepath = ''
        
        self.bufferSeconds = 5

        self.startTime = 0 #when we start recording in run(), triggered by startVideo()
        self.recordDuration = float('inf') #10 #seconds, set to infinity to then stop with stopVideo()
        
        self.doTimelapse = 0
        self.stillinterval = 5 #second
        self.lastimage = ''
        
        #set up local parameter
        self.config = {}
        self.config['camera'] = {}
        self.config['camera']['fps'] = 30
        self.config['camera']['resolution'] = (640, 480)
        
        self.config['triggers'] = {}
        self.config['triggers']['useTwoTriggerPins'] = True
        self.config['triggers']['triggerpin'] = 27
        self.config['triggers']['framepin'] = 17

        #fill in parameters from config.ini
        self.ParseConfigFile()
        
        triggerpin = self.config['triggers']['triggerpin']
        framepin = self.config['triggers']['framepin']

        GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  

        GPIO.setup(self.config['triggers']['triggerpin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    #
        GPIO.setup(self.config['triggers']['framepin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    #

        if self.config['triggers']['useTwoTriggerPins']:
            print 'two pin style triggerpin is', triggerpin
            print 'two pin style framepin is', framepin
            GPIO.add_event_detect(triggerpin, GPIO.BOTH, callback=self.triggerPinCallback) #, bouncetime=10)
            GPIO.add_event_detect(framepin, GPIO.RISING, callback=self.framePinCallback) #, bouncetime=10)
        else:
            print 'scanimage style triggerpin is', triggerpin
            GPIO.add_event_detect(triggerpin, GPIO.BOTH, callback=self.scanimageCallback) #, bouncetime=10)
            
        self.lastFrameTime = 0 # set in newFrame() and checked in main run loop for stop condition
        self.lastFrameTimeout = 1 # seconds
        
        self.scanImageFrame = 0
        
        #keep a list of frame,time
        self.frameList = []
        
    def ArmTrigger(self):
    	self.daemon = True
    	self.start()
    	self.startArm()
    	
    '''
    one callback for complex scanimage frame clock
    this is a really bad solution that just assumes ANY change on pin
    problem is when pulse is really fast, down on frame then reading for down will miss it and read an up
    '''
    def scanimageCallback(self, pin):
        pinIsUp = GPIO.input(pin)
        timeSeconds = time.time()
        if pinIsUp and not self.videoStarted:
             self.startVideo()
        elif not pinIsUp and self.videoStarted:
             self.newFrame(timeSeconds)
             
    '''
    two callbacks for two pin configuration (i) trigger and (ii) frame
    '''
    def triggerPinCallback(self, pin):
        timeSeconds = time.time()
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
            print 'ParseConfigFile() not alowed while isArmed'
            return
            
        print 'reading config file from config.ini'

        Config = ConfigParser.ConfigParser()
        Config.read('config.ini')
        Config.sections()
		
        self.config['camera']['fps'] = int(Config.get('camera','fps'))
        
        resolution = Config.get('camera','resolution').split(',')
        self.config['camera']['resolution'] = (int(resolution[0]), int(resolution[1]))		
        
        self.config['triggers']['useTwoTriggerPins'] = int(Config.get('triggers','useTwoTriggerPins'))
        self.config['triggers']['triggerpin'] = int(Config.get('triggers','triggerpin'))
        self.config['triggers']['framepin'] = int(Config.get('triggers','framepin'))

        print 'done reading config file'
		    
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
            
    def startArm(self):
        print '\tVideoThread startArm()'
        if self.isArmed == 0:
            try:
                print '\tVideoServer initializing camera'
                self.camera = picamera.PiCamera()
                self.camera.resolution = (640, 480)
                #self.camera.led = 0
                self.camera.start_preview()
                self.camera.framerate = self.config['camera']['fps']
            
                print '\tVideoServer.startArm() starting circular stream'
                self.stream = picamera.PiCameraCircularIO(self.camera, seconds=self.bufferSeconds)
                self.camera.start_recording(self.stream, format='h264')

                self.isArmed = 1 #order is important, must come after we instantiate camera
        
            #except PiCameraMMALError:
            #    print 'startArm() error: PiCameraMMALError'
            except:
                print 'startArm() error'
                
    def stopArm(self):
        print '\tVideoThread stopArm()'
        timestamp = self.GetTimestamp()
        if self.isArmed == 1:
            self.isArmed = 0
            
            self.camera.stop_preview()
            self.camera.close()
            self.camera = None
            
            self.logfileWrite(timestamp, 'VideoServerStopArm', None)
            self.logFileName = ''
            self.scanImageFrame = 0
            print '\tVideoServer stopArm() is done'

    def startVideo(self):
        '''
        todo: add parameter for recordDuration
        '''
        timestamp = self.GetTimestamp2()
        if self.isArmed and not self.videoStarted:
            print timestamp, 'startVideo()'
            self.recordDuration = float('inf') #5 #seconds, make this a parameter
            self.savename = timestamp.split('.')[0]
            self.scanImageFrame = 0
            self.videoStarted = 1
            self.logfileWrite(timestamp, 'VideoStart', None)
            if self.camera:
                self.camera.annotate_text = 'S'
                self.camera.annotate_background = picamera.Color('black')
            
            #remove fractional seconds
            self.logFileName = self.savename + '_si.txt'
            self.logFilePath = self.savepath + self.logFileName
            self.logfileWrite(timestamp, 'startVideo', None)

            self.frameList = []

    def stopVideo(self):
        timestamp = self.GetTimestamp2()
        if self.isArmed and self.videoStarted:
            print timestamp, 'stopVideo()'
            self.videoStarted = 0
            if self.camera:
                self.camera.annotate_text = ''
                self.camera.annotate_background = None

            print 'writing log file once'
            with open(self.logFilePath, 'a') as textfile:
                textfile.write("date,time,seconds,frame\n")
            with open(self.logFilePath, 'a') as textfile:
                for item in self.frameList:
                    textfile.write("%s\n" % item)

            #self.logfileWrite(timestamp, 'stopVideo', None)
            self.logFileName = ''
            self.logFilePath = ''
  
    def newFrame(self, timeSeconds):
        '''
        timeSeconds: time.time()
        '''
        localtime = time.localtime(timeSeconds)
        dateStr = time.strftime('%Y%m%d',localtime)
        timeStr = time.strftime('%H%M%S', localtime) #expand this to have fraction
        
        self.lastFrameTime = timeSeconds
        self.scanImageFrame += 1
        self.camera.annotate_text = str(self.lastFrameTime) + ' ' + str(self.scanImageFrame)
        print dateStr, timeStr, 'scanImageFrame is', self.scanImageFrame
        
        listLine = dateStr + ',' + timeStr + ',' + str(self.lastFrameTime) + ',' + str(self.scanImageFrame)
        self.frameList.append(listLine)
          
    #when creating this file, append a header with #fps=xxx,width=xxx,y=yyy
    def logfileWrite(self, timestamp, myStr, myVal):
        1
        #if self.logFilePath:
        #    with open(self.logFilePath, 'a') as textfile:
        #        textfile.write(str(timestamp) + ',' + myStr + ',' + str(myVal) + '\n')

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
                timestamp = self.GetTimestamp()
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
                                #this is for single trigger/frame pin in ScanImage
                                if not useTwoTriggerPins and (time.time() > (self.lastFrameTime + self.lastFrameTimeout)):
                                    print 'run() is stopping after last frame timeout'
                                    stopOnTrigger = 1
                                
                            self.stopVideo() #
                            self.camera.split_recording(self.stream)
                            print '\tVideoServer received self.videoStarted==0 or past recordDuration'
                            #self.sendtoserver()
                        
                        #capture a foo.jpg frame every stillInterval seconds
                        thistime = time.time()
                        if self.doTimelapse and thistime > (lasttime+self.stillinterval):
                            lasttime = thistime
                            self.lastimage = self.GetTimestamp() + '.jpg'
                            print 'capturing still frame:', self.lastimage
                            self.camera.capture(self.savepath + self.lastimage, use_video_port=True)
            
                        time.sleep(0.001) # seconds
                    except:
                        print '\tVideoServer except clause -->>ERROR'
                print '\tVideoServer.run() fell out of while(self.isArmed) loop'
            time.sleep(0.05)
        print '\tVideoServer.run() terminating [is never called]'
        
        #i should wrap this in a try: except: finally:
        if self.camera:
            self.camera.close
        GPIO.cleanup()