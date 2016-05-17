## Trigger Camera

This is a Raspberry Pi camera that can be configured to respond to digital TTL pulses to start and stop video acquisition during an experiment. During video acquisition, external events such as frame times on a scanning microscope are watermarked on the video and saved to a text file.

The camera can be controlled from a Python command prompt, via a web browser, or using a hardware LCD/keypad.

## Configuring a Raspberry Pi

We are not going to provide a full tutorial here and assume you have a functioning raspberry pi. Here are some useful things to get you started

 - Install Raspbian on an SD card and boot your pi
 - Configure wired network
 - Make sure the camera is installed
 - Install required python libraries
 - SMB to mount/share folders with Windows computers
 - AFP to mount/share folder with OS X
 - StartUpMailer to have the Raspberry Pi email with its IP address when it boots
 
## Required Python libraries

### Python interface

    RPi.GPIO
    picamera
    ConfigParser

### Flask Interface

    flask
    flask-socketio
    
## Camera Interface

### Python command line

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

### Web

[triggercamera_app.py][triggercamera_app] provides a webserver allowing the camera to be controlled through a web browser. The web server is run using [Flask][flask] and provides a REST api as a wrapper around the triggercamera.py command line engine.

Run the Flask server with

    python triggercamera_app.py
    
The server will be available on the local IP address of the machine running the code, in this case '192.168.1.12'. The server will run on port 5010.

Then, the camera can be controled through a web browser as follows.

    http://192.168.1.12:5010/startarm
    http://192.168.1.12:5010/stoparm
    http://192.168.1.12:5010/startvideo
    http://192.168.1.12:5010/stopvideo
    http://192.168.1.12:5010/timelapseon
    http://192.168.1.12:5010/timelapseoff
    http://192.168.1.12:5010/lastimage

**todo**: add an actual webpage with buttons to control the camera and give realtime feedback

### LCD and keypad

NOT IMPLEMENTED. A hardware interface is provided if an [LCD/keypad][lcdkeypad] is attached to the Raspberry Pi.

     
## User configuration

Modify config.txt and restart the camera code

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

See this to auto mount SMB share on boot

    http://raspberrypi.stackexchange.com/questions/34444/cant-get-a-cifs-network-drive-to-mount-on-boot
    
[piicamera]: http://picamera.readthedocs.io/en/release-1.10/
[configparser]: https://docs.python.org/2/library/configparser.html
[flask]: http://flask.pocoo.org
[flask socketio]: http://flask-socketio.readthedocs.io/en/latest/

[lcdkeypad]: https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi

[config.txt]: https://github.com/cudmore/timelapsecamera/blob/master/config.txt
[triggercamera]: https://github.com/cudmore/timelapsecamera/blob/master/triggercamera.py
[triggercamera_app]: https://github.com/cudmore/timelapsecamera/blob/master/triggercamera_app.py
