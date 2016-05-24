Please see the most up to date documentation at: [Trigger Camera Documetation][docs]

# Trigger Camera

This is a Raspberry Pi camera that responds to general purpose digital input-output (GPIO) pulses to start and stop video acquisition during an experiment. During video acquisition, external events such as frame times on a scanning microscope are watermarked on the video and saved to a text file. The camera can be controlled from a Python command prompt, via a web browser, or using a hardware LCD/keypad.

<IMG SRC="/docs/img/triggercamera-minimized2.png" WIDTH=450 style="border:1px solid gray">

### triggercamera.py

Allows interaction through a Python command prompt.  Run with `python triggercamera.py`.

	import triggercamera
	tc=triggercamera.TriggerCamera()
	tc.ArmTrigger()

### triggercamera_app.py

Runs a web server to allow camera to be controlled through a web browser.

	http://192.168.1.12:5010/help
	http://192.168.1.12:5010/startarm
	http://192.168.1.12:5010/stoparm
	http://192.168.1.12:5010/startvideo
	http://192.168.1.12:5010/stopvideo
	http://192.168.1.12:5010/timelapseon
	http://192.168.1.12:5010/timelapseoff
	http://192.168.1.12:5010/lastimage

### config.ini

Main configuration file to control how Trigger Camera behaves.

	[triggers]
	useTwoTriggerPins: 1
	triggerpin: 27
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

### /analysis/

Example iPython/Jupyter notebook to load output .txt files and measure the performance of the camera.

### /testing/

Arduino code that simulates hardware by setting GPIO pins for start/stop trial and frame.

### /docs/

The full documentation for this project written in markdown and served [here][docs].

[docs]: http://cudmore.github.com/triggercamera
