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
        self.recordDuration = 10 #seconds, set to infinity to then stop with stopVideo()
        
        self.doTimelapse = 0
        self.stillinterval = 5 #second
        self.lastimage = ''
        
        #set up local parameter
        self.config = {}
        self.config['camera'] = {}
        self.config['camera']['fps'] = 30
        self.config['camera']['resolution'] = (640, 480)
        
        self.config['triggers'] = {}
        self.config['triggers']['triggerpin'] = 1
        self.config['triggers']['framepin'] = 2

        #fill in parameters from config.ini
        self.ParseConfigFile()
        
        #self.Config.get('Person','HasEyes')
        #self.Config.set('Person','HasEyes',True)
        #self.Config['camera'].resolution = (640, 480)
        #self.Config['camera'].fps = 30 # 30, 60, 90
        
        #self.triggerPin = 2
        self.framePin = 3
        GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
        #GPIO.setup(self.triggerPin, GPIO.IN)    # set GPIO25 as input (button)  
        GPIO.setup(self.framePin, GPIO.IN)    # set GPIO25 as input (button)  
        #GPIO.add_event_detect(self.triggerPin, GPIO.BOTH, callback=self.triggerCallback, bouncetime=10)
        #GPIO.add_event_detect(self.framePin, GPIO.BOTH, callback=self.frameCallback, bouncetime=10)
        GPIO.add_event_detect(self.framePin, GPIO.BOTH, callback=self.framePinCallback, bouncetime=10)

        self.lastFrameTime = 0 # set in newScanImageFrame() and checked in main run loop for stop condition
        self.lastFrameTimeout = 1 # seconds
        
        self.scanImageFrame = 0
        
    def ArmTrigger(self):
    	self.daemon = True
    	self.start()
    	self.startArm()
    	
    # one callback for complex scanimage frame clock
    def framePinCallback(self, pin):
        isUp = GPIO.input(self.framePin)
        print 'framePinCallback()', isUp
        timestamp = self.GetTimestamp()
        if isUp and not self.videoStarted:
            #print 'framePinCallback() calling startVideo()'
            self.startVideo()
        elif not isUp and self.videoStarted:
            #print 'framePinCallback() calling newScanImageFrame()'
            self.newScanImageFrame(timestamp)
            
    '''
    def triggerCallback(self, pin):
        isUp = GPIO.input(self.triggerPin)
        print 'triggerCallback() got', isUp
        if isUp and self.isArmed and not self.videoStarted:
            print 'triggerCallback should start'
            self.startVideo()
        elif not isUp and self.isArmed and self.videoStarted:
            print 'triggerCallback should stop'
            self.stopVideo()
        
    def frameCallback(self, pin):
        isUp = GPIO.input(self.framePin)
        print '    frameCallback', isUp
        timestamp = self.GetTimestamp()
        #self.newScanImageFrame(timestamp)    
    '''
    
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
            self.recordDuration = 5 #seconds, make this a parameter
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

    def stopVideo(self):
        timestamp = self.GetTimestamp2()
        if self.isArmed and self.videoStarted:
            print timestamp, 'stopVideo()'
            self.videoStarted = 0
            if self.camera:
                self.camera.annotate_text = ''
                self.camera.annotate_background = None
            self.logfileWrite(timestamp, 'stopVideo', None)
            self.logFileName = ''
            self.logFilePath = ''

    def newScanImageFrame(self, timestamp):
        self.lastFrameTime = time.time()
        self.scanImageFrame += 1
        print timestamp, 'scanImageFrame is', self.scanImageFrame
        self.logfileWrite(timestamp, 'frame', self.scanImageFrame)
           
    #when creating this file, append a header with #fps=xxx,width=xxx,y=yyy
    def logfileWrite(self, timestamp, myStr, myVal):
        if self.logFilePath:
            with open(self.logFilePath, 'a') as textfile:
                textfile.write(str(timestamp) + ',' + myStr + ',' + str(myVal) + '\n')

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
                                self.camera.wait_recording(0.001)
                                if not GPIO.input(self.framePin) and (time.time() > (self.lastFrameTime + self.lastFrameTimeout)):
                                    print 'run() is stopping after last frame'
                                    stopOnTrigger = 1
                                
                            self.stopVideo() #
                            self.camera.split_recording(self.stream)
                            print '\tVideoServer received self.videoStarted==0 or past recordDuration'
                            #self.sendtoserver()
                        
                        #check if we received down on scanimage frame pin and if it has been some time
                        #if time.time() > (self.lastFrameTime + self.lastFrameTimeout):
                        #    #scanimage frame clock pin has been down awhile
                        #    print 'run() is calling stopVideo() after last frame'
                        #    self.stopVideo()
                        
                        #capture a foo.jpg frame every stillInterval seconds
                        thistime = time.time()
                        if self.doTimelapse and thistime > (lasttime+self.stillinterval):
                            lasttime = thistime
                            self.lastimage = self.GetTimestamp() + '.jpg'
                            print 'capturing still frame:', self.lastimage
                            self.camera.capture(self.savepath + self.lastimage, use_video_port=True)
            
                        #self.beforefilename = ''
                        #self.afterfilename = ''
                        #self.beforefilepath = ''
                        #self.afterfilepath = ''
                    except:
                        print '\tVideoServer except clause -->>ERROR'
                print '\tVideoServer.run fell out of loop'
            time.sleep(0.05)
        print '\tVideoServer terminating [is never called]'
        
        #i should wrap this in a try: except: finally:
        if self.camera:
            self.camera.close
        GPIO.cleanup()