# Author: Robert H Cudmore
# Web: http://robertcudmore.org
# Date: 20151205

'''
todo
	- add dio to start/stop
	- add dio to add a frame # to frames
'''

'''
Purpose: A circular video stream that can start/stop video acquisition

ToDo
==========
Add low level interrupts to start/stop video

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

class VideoServer(threading.Thread):
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
        
    def getState(self):
        ret = 'a=b'
        ret += '\nc=d'
        return ret
        
    def startArm(self):
        print '\tVideoThread startArm()'
        if self.isArmed == 0:
            print '\tVideoServer initializing camera'
            self.camera = picamera.PiCamera()
            self.camera.resolution = (640, 480)
            #self.camera.led = 0
            self.camera.start_preview()
            self.camera.framerate = 30 # can be 60
            
            print '\tVideoServer starting circular stream'
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
            
            self.logfileWrite(timestamp, 'VideoServerStopArm')
            self.logFileName = ''
            self.scanImageFrame = 0
            print '\tVideoServer stopArm() is done'

    def startVideo(self):
        '''
        todo: add parameter for recordDuration
        '''
        timestamp = self.GetTimestamp2()
        if self.isArmed and not self.videoStarted:
            self.recordDuration = 5 #seconds, make this a parameter
            self.savename = timestamp.split('.')[0]
            self.scanImageFrame = 0
            self.videoStarted = 1
            self.logfileWrite(timestamp, 'VideoStart')
            if self.camera:
                self.camera.annotate_text = 'S'
                self.camera.annotate_background = picamera.Color('black')
            
            #remove fractional seconds
            self.logFileName = self.savename + '_si.txt'
            self.logFilePath = self.savepath + self.logFileName
            self.logfileWrite(timestamp, 'startVideo')

    def stopVideo(self):
        timestamp = self.GetTimestamp2()
        if self.isArmed and self.videoStarted:
            self.videoStarted = 0
            if self.camera:
                self.camera.annotate_text = ''
                self.camera.annotate_background = None
            self.logfileWrite(timestamp, 'stopVideo')
            self.logFileName = ''
            self.logFilePath = ''

    def logfileWrite(self, timestamp, myStr):
        if self.logFilePath:
            with open(self.logFilePath, 'a') as textfile:
                textfile.write(str(timestamp) + '\t' + myStr + '\n')

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
        while True:
            if self.isArmed:
                timestamp = self.GetTimestamp()
                while (self.isArmed):
                    try:
                        self.camera.wait_recording(0.005)
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
                
                            while self.videoStarted and (time.time()<(self.startTime + self.recordDuration)):
                                self.camera.wait_recording(0.001)
                
                            self.stopVideo() #
                            self.camera.split_recording(self.stream)
                            print '\tVideoServer received self.videoStarted==0 or past recordDuration'
                        
                        #capture a foo.jpg frame every stillInterval seconds
                        thistime = time.time()
                        if self.doTimelapse and thistime > (lasttime+self.stillinterval):
                            lasttime = thistime
                            self.lastimage = self.GetTimestamp() + '.jpg'
                            print 'capturing still frame:', self.lastimage
                            self.camera.capture(self.savepath + self.lastimage, use_video_port=True)
            
                        self.beforefilename = ''
                        self.afterfilename = ''
                        self.beforefilepath = ''
                        self.afterfilepath = ''
                    except:
                        print '\tVideoServer except clause -->>ERROR'
                print '\tVideoServer.run fell out of loop'
            time.sleep(0.05)
        print '\tVideoServer terminating [is never called]'