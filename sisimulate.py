#simulate scan image start/stop and frame pin

import time
import RPi.GPIO as GPIO

'''
triggerPin = 14
framePin = 15

GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
GPIO.setup(triggerPin, GPIO.OUT)    # set GPIO25 as input (button)  
GPIO.setup(framePin, GPIO.OUT)    # set GPIO25 as input (button)  

def run():
    GPIO.output(triggerPin, 0)
    GPIO.output(framePin, 0)

    delaySeconds = 0.2 #sec
    numFrames = 10
    currentFrame = 1
    frameInterval = 0.1 #seconds

    startSeconds = time.time() #seconds
    lastFrameSeconds = 0
    started = False

    done = False
    while not done:
        now = time.time()
        if now > (startSeconds + delaySeconds):
            if not started:
                started = True
                print now, 'started'
                GPIO.output(triggerPin, 1)
            if now > (lastFrameSeconds + frameInterval):
                lastFrameSeconds = now
                currentFrame += 1
                print now, 'frame', currentFrame
                GPIO.output(framePin, 1)
                GPIO.output(framePin, 0)
                if currentFrame > numFrames:
                    done = True

    GPIO.output(triggerPin, 0)
    GPIO.output(framePin, 0)
'''

framePin = 15
GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
GPIO.setup(framePin, GPIO.OUT)    # set GPIO25 as input (button)  

def run():
    GPIO.output(framePin, 0)

    delaySeconds = 0.2 #sec
    numFrames = 10
    currentFrame = 1
    frameInterval = 0.1 #seconds

    startSeconds = time.time() #seconds
    lastFrameSeconds = 0
    started = False

    done = False
    while not done:
        now = time.time()
        if now > (startSeconds + delaySeconds):
            if not started:
                started = True
                print now, 'started'
                GPIO.output(framePin, 1)
            elif now > (lastFrameSeconds + frameInterval):
                lastFrameSeconds = now
                currentFrame += 1
                print now, 'frame', currentFrame
                GPIO.output(framePin, 0)
                time.sleep(0.005)
                GPIO.output(framePin, 1)
                if currentFrame > numFrames:
                    done = True
        time.sleep(0.005)

    print now, 'stopped'
    GPIO.output(framePin, 0)
