## Trigger Camera

This is a Raspberry Pi camera that responds to digital TTL pulses to start and stop video acquisition during an experiment. During video acquisition, external events such as frame times on a scanning microscope are watermarked on the video and saved to a text file.

The camera can be controlled from a Python command prompt, via a web browser, or using a hardware LCD/keypad.

## Overview

The Raspberry Pi is a low cost ($35) computer that runs Linux. In addition to USB, ethernet, and HDMI connectors, the Raspberry Pi has a dedicated camera port and low level digital input and output (DIO). Both the camera and DIO pins can be programmed easily using Python.

Once the camera is armed, it will continuously record a circular stream of video in memory. When a trigger is received, the the video will begin being saved to disk. In addition to saving the video after a trigger, the video before the trigger will also be saved. This has the distinct advantage of given you a record of what your animal was doing  before a trial was started. In many cases, 'bad trials' can be found because there was a lot of movement (or some other abberent event) before a trial began.

## Parts list

These parts are widely available at many different online sellers including: Sparkfun, Adafruit, Element14, and Amazon.

 - Raspberry Pi 2 or 3
 - SD card
 - Power supply
 - USB stick to save video
 - Voltage level shifter
 - Raspberry Pi NoIR camera
 - Pi camera ribbon cables (2 meters)
 - IR LEDS
 - Cables to wire the Raspberry Pi to digital lines
 - Pi Camera ribbon cable to HDMI converter
 - [optional] 5V relay to allow Pi to switch higher voltage power (5V or 12V) on/off
 
While the cost of the Pi is cheap, the price adds up with all the additional pieces needed. In the end, the total cost should be $100 to $150.

The Raspberry Pi can only accept digital signals at 3.5V. Many devices use 5V for digital signals. Thus, a level shifter is needed to convert 5V to 3.5V. This can be easily wired by hand as a voltage divider or purchased as a premade circuit board.

## Configuring a Raspberry Pi

We are not going to provide a full tutorial here and assume you have a functioning Raspberry Pi. Here is a basic to do list to get started.

 - Install Raspbian on an SD card and boot the pi
 - Configure wired network
 - Make sure the camera is installed
 - Install required python libraries
 - SMB to mount/share folders with Windows computers
 - AFP to mount/share folders with OS X (SMB will also work with OS X)
 - StartUpMailer to have the Raspberry Pi email with its IP address when it boots

## Wiring the system

 - Connect Camera to Raspberry Pi
 - Connect digital lines to the Raspberry Pi (be sure to convert 5V lines to 3.5V)
 - Ground the Raspberry Pi to the digital line ground/shield
 - Connect LEDs to the Raspberry Pi. If LEDs need a lot of power, hook them up with a 5V relay.
 
## Required Python libraries

### Python interface

    RPi.GPIO
    picamera
    ConfigParser

### Web Interface

    flask
    flask-socketio

## Camera Interface

### Python command line interface

With [triggercamera.py][triggercamera], the camera can be controlled with a python command line interface. Once the camera is armed with 'ArmTrigger()' it will start and stop video recording following a TTL trigger.

	import triggercamera
	tc=triggercamera.TriggerCamera()
	tc.ArmTrigger()

Additional interface

	#start and stop video recording as much as you like
	tc.startVideo()
	tc.stopVideo()

	# single images can be saved every few seconds while video is being recorded
	tc.doTimelapse=1
	tc.doTimelapse=0

### Web interface

[triggercamera_app.py][triggercamera_app] provides a web server allowing the camera to be controlled through a web browser. The web server is run using [Flask][flask] and provides a REST api as a wrapper around the triggercamera.py command line engine.

Run a web server with

    python triggercamera_app.py

The server will be available on the local IP address of the machine running the code, in this case '192.168.1.12'. The server will run on port 5010.

The camera can be controlled through a web browser as follows.

    http://192.168.1.12:5010/startarm
    http://192.168.1.12:5010/stoparm
    http://192.168.1.12:5010/startvideo
    http://192.168.1.12:5010/stopvideo
    http://192.168.1.12:5010/timelapseon
    http://192.168.1.12:5010/timelapseoff
    http://192.168.1.12:5010/lastimage

**to do:** Add an actual web page with buttons to control the camera and give realtime feedback.

### LCD and keypad interface

**NOT IMPLEMENTED.** A hardware interface is provided if an [LCD/keypad][lcdkeypad] is attached to the Raspberry Pi.


## User configuration

Modify [config.ini][config.ini] and restart the camera code

	[triggers]
	triggerpin: 1
	framepin: 2

	[camera]
	fps: 30
	resolution: 640,480
	bufferSeconds = 5

## Troubleshooting

Test the camera with

    raspistill -o tst.jpg

If the camera triggering is erratic or the Raspberry is missing fast pulses, check that all digital lines going to the Raspberry Pi are grounded. It is good practice to connect the Raspberry Pi ground pins to the ground (shield) of any digital lines.

See this to auto mount an SMB share on boot

   http://raspberrypi.stackexchange.com/questions/34444/cant-get-a-cifs-network-drive-to-mount-on-boot

## To Do
 - Implement a Flask homepage to provide buttons to control camera and feedback during a trial.
 - Add control and interface for two LEDs (e.g. IR and white).
 
[piicamera]: http://picamera.readthedocs.io/en/release-1.10/
[configparser]: https://docs.python.org/2/library/configparser.html
[flask]: http://flask.pocoo.org
[flask socketio]: http://flask-socketio.readthedocs.io/en/latest/

[lcdkeypad]: https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi

[config.ini]: https://github.com/cudmore/triggercamera/blob/master/config.ini
[triggercamera]: https://github.com/cudmore/triggercamera/blob/master/triggercamera.py
[triggercamera_app]: https://github.com/cudmore/triggercamera/blob/master/triggercamera_app.py
