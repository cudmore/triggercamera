# Trigger Camera

This is a Raspberry Pi camera that responds to digital TTL pulses to start and stop video acquisition during an experiment. During video acquisition, external events such as frame times on a scanning microscope are watermarked on the video and saved to a text file.

The camera can be controlled from a Python command prompt, via a web browser, or using a hardware LCD/keypad.

# Overview

## Background on the Raspberry Pi

The Raspberry Pi is a low cost ($35) computer that runs Linux. In addition to USB, ethernet, and HDMI connectors, the Raspberry Pi has a dedicated camera port and low level digital input and output (DIO). Both the camera and DIO pins can be easily programmed  using Python.

The Raspberry Pi provides an end-to-end open source system. Both the hardware and the software is provided by [The Raspberry Pi Foundation][raspberrypi.org] and an active developer community. Given that all components are open-source, there are some very unique upgrades that one does not see in a commercial marketplace. The Raspberry Pi computer itself has undergone three rounds of system upgrades, increasing its processor speed by more than a factor of ten, expanding its onboard RAM, and adding onboard WIFI and Bluetooth while the price has remained fixed at $35. When it was first released, the 5MP Raspberry Pi camera could record 640x480 video at 30 frames-per-second. With a software upgrade this capability was extended to 60 and 90 frames per second and a second camera was then released increasing the sensor size from 5MP to 8MP while keeping the price fixed at $25.

## Software implementation

The software provided here will run a Raspberry Pi camera as a slave to other devices already in place for an experiment.

Once the camera is armed, it will continuously record a circular stream of video in memory. When a digital trigger is received, the the video will begin being saved to disk. In addition to saving the video after a trigger, the video before the trigger will also be saved. This has the distinct advantage of given you a record of what your animal was doing  before a trial was started. In many cases, 'bad trials' can be found because there was a lot of movement (or some other abberent event) before a trial began.

# Parts list

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

# Configuring a Raspberry Pi

We are not going to provide a full tutorial here and assume you have a functioning Raspberry Pi. Here is a basic to do list to get started.

 - Install Raspbian on an SD card and boot the pi
 - Configure wired network
 - Make sure the camera is installed
 - Install required python libraries
 - SMB to mount/share folders with Windows computers
 - AFP to mount/share folders with OS X (SMB will also work with OS X)
 - StartUpMailer to have the Raspberry Pi email with its IP address when it boots

# Building the system

## Wiring the system

 - Connect Camera to Raspberry Pi
 - Connect digital lines to the Raspberry Pi (be sure to convert 5V lines to 3.5V)
 - Ground the Raspberry Pi to the digital line ground/shield
 - Connect LEDs to the Raspberry Pi. If LEDs need a lot of power, hook them up with a 5V relay.

## Installing required Python libraries

### Python interface

    RPi.GPIO
    picamera
    ConfigParser

### Web Interface

    flask
    flask-socketio

# Limitations

The Raspberry Pi runs Linux and like other operating systems including Microsoft Windows and Mac OS it is not real time. There will always be unpredictable delays in the detection and generation of digital pulses. If the detection of a fast pulse or the timing of a pulse is critical for an experiment it is strongly suggested to use a more precise microcontroller like an Arduino.

See the **Analysis** section for example Python code to test the limits of this precision.

# Running the camera

## Python command line interface

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

	# todo: add interface to control two different LEDs

## Web interface

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

## LCD and keypad interface

**NOT IMPLEMENTED.** A hardware interface is provided if an [LCD/keypad][lcdkeypad] is attached to the Raspberry Pi.


# User configuration

Modify [config.ini][config.ini] and restart the camera code

	[triggers]
	triggerpin: 4
	framepin: 17

	[led]
	led1pin: 2
	led2pin: 3

	[camera]
	fps: 30
	resolution: 640,480
	bufferSeconds = 5

	watchedpathon: 1
	watchedpath: /video

	savepath: /video

# Output video

Trigger camera saves video in the [h264][h264] video format. This is a very efficient video codec that make very small but highly detailed videos. Before you analyze these h264 video files they need to be converted to include the frames per second. This can be done in a number of video editing programs but we suggest [ffmpeg][ffmpeg] because it can be scripted and incorporated into most workflows.

**to do** Supply real ffmpeg code

    srcDir = '/src/dir/with/video'
    dstDir = 'dst/dir/for/mp4'
    for file in srcDir:
        outfile = file.strip('h264') + '.mp4'
        ffmpeg -r 25 -i file dstDir+outfile

# Output files

In addition to saving video, Trigger Camera also saves a .txt file for each video with frame time stamps.

Here are the first 5 frames of an output .txt file

    date,time,seconds,frame
    20160520,074319.0,1463744599.61,1
    20160520,074319.0,1463744599.65,2
    20160520,074319.0,1463744599.68,3
    20160520,074319.0,1463744599.71,4
    20160520,074319.0,1463744599.74,5

**to do** ADD A HEADER LINE WITH FPS and VIDEO WIDTH/HEIGHT PLUS OTHER PARAMETERS.

# Analysis

We have provided Python code to load, analyze and plot these output .txt file. See [an example iPython notebook][analysis.ipynb]

<IMG SRC="img/analysis_v2.png">

# Troubleshooting

 - Test the camera with

    raspistill -o tst.jpg

 - If the camera triggering is erratic or the Raspberry is missing fast pulses, check that all digital lines going to the Raspberry Pi are grounded. It is good practice to connect the Raspberry Pi ground pins to the ground (shield) of any digital lines.

 - If the recorded video changes light-levels erratically, this is usllay due to fluctuations in the power to the Pi. Make sure the Pi has a DC power supply >2 Amps. If additional LEDs are being powered by the Pi, consider breaking these out with their own dedicated power supplies.

 - See this to auto mount an SMB share on boot

   http://raspberrypi.stackexchange.com/questions/34444/cant-get-a-cifs-network-drive-to-mount-on-boot

## To Do
 - Implement a Flask homepage to provide buttons to control camera and feedback during a trial.
 - Add control and interface for two LEDs (e.g. IR and white).

 - try using easydict so i can use'.' notation in code

[raspberrypi.org]: https://www.raspberrypi.org
[piicamera]: http://picamera.readthedocs.io/en/release-1.10/
[configparser]: https://docs.python.org/2/library/configparser.html
[flask]: http://flask.pocoo.org
[flask socketio]: http://flask-socketio.readthedocs.io/en/latest/

[lcdkeypad]: https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi

[config.ini]: https://github.com/cudmore/triggercamera/blob/master/config.ini
[triggercamera]: https://github.com/cudmore/triggercamera/blob/master/triggercamera.py
[triggercamera_app]: https://github.com/cudmore/triggercamera/blob/master/triggercamera_app.py

[analysis.ipynb]: https://github.com/cudmore/triggercamera/blob/master/analysis/analysis_v1.ipynb
[analysis]: https://github.com/cudmore/triggercamera/tree/master/analysis
[ffmpeg]: https://ffmpeg.org
[h264]: https://en.wikipedia.org/wiki/H.264/MPEG-4_AVC
