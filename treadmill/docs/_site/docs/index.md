# 
# Introduction

Controlling an experiment with an Arduino microcontroller has become commonplace in scientific labs. A major bottle-neck in making experiments controlled with an Arduino main-stream is the difficulty in their use. Once embedded into an experiment, the control of an Arduino often involves cognitively-demanding command line interaction which detracts from potentially complicated experiments. Thus, a simplified interface to control an Arduino during an experiment is necessary.

Here, we present a simplified and experimentally fool-proof web interface to control an Arduino using a point-and-click web interface. In particular, we have built a motorized treadmill for in vivo head-fixed two-photon imaging. We provide schematics for building the treadmill as well as Arduino and Python code to control the treadmill.

This is a general-purpose open-source framework where Arduino based experiments can be controlled through a web interface. The source-code can be easily modified to meet new and unique experimental designs.


## Web Interface

<IMG SRC="img/screenshot1.png" WIDTH=450 style="border:1px solid gray">

The top section provides an interface to start/stop a trial and plots real-time feedback as the trial is running.

The middle section provides an interface to set stimulus parameters for a trial and to upload these parameters to an Arduino. This section also provides a plot of what the trial will look like based on the set of parameters entered.


## Arduino Setup

###  Hardware

- Arduino Uno

- Stepper Motor, [Sparkfun - 09238][7], $15

- Stepper motor driver, EasyDriver, [Sparkfun - 12779][8], $15. Main website for [EasyDriver][9]

- Rotary encoder, [Honeywell-600-128-CBL][10], [.pdf][11] spec sheet, $37

- IR LED, 840-850 nm, [Sparkfun - 9469][12] $1 each (960 nm IR LEDs do not work well with Pi Noir camera)

- Actobotics at [ServoCity][13] and [Sparkfun][14]. Give [ServoCity][15] a shot, their visual guides and project ideas are really helpful in desining components. This can be your one stop shop for all structural components including frames, rods, bearings, clamps, and motor mounts.

###  Wiring the arduino

- Wire the stepper motor
- Wire the stepper motor to the stepper motor driver
- Wire the rotary encoder
- Wire the DIO pins to communicate with ScanImage

## Upload code to the Arduino

###  Required libraries

You want to use these non-blocking libraries otherwise your code will not perform well. If you don't use these libraries then code to turn the stepper motor will block other code like reading the rotary encoder. 

- [AccelStepper][16] library to control stepper motor

- Rotary encoder library from [PJRC][17]

###  Upload using the Arduino IDE

The source code for the Arduino can be found in [/arduino/src/treadmill.cpp][4].

Use the standard Arduino IDE to upload treadmill.cpp to your Arduino. Make sure you have the required Arduino libraries installed. Also be sure you understand how to activate addition [low level interrupts](index.md#lowlevelinterrupts) if using an Arduino Uno.

### Upload using platformio

If you prefer you can use [Platformio][5] to do everything from a command line. This has the distinct advantage that you can compile and upload code from a headless computer including a Raspberry Pi or any system running Linux.

Platformio is a python library so you should be good to go with `pip install platformio`. 

Have a look [here][6] to create a platformio.ini file for your specific Arduino. Here are three different board configurations

```
platformio init --board uno # arduino uno
platformio init --board pro16MHzatmega328 # generic arduino pro 
platformio init --board nodemcuv2 # arduino node mcu
```

After 'platformio init', platformio.ini will have environment configurations. You only want to have one of these blocks at a time to simplify compilation. For example [env:uno].

```
[env:uno]
platform = atmelavr
framework = arduino
board = uno
build_flags = -D _expose_interrupts_ #creates compiler directive

[env:pro16MHzatmega328]
platform = atmelavr
framework = arduino
board = pro16MHzatmega328

[env:nodemcuv2]
platform = espressif
framework = arduino
board = nodemcuv2
upload_port = /dev/ttyUSB0

```

Compile, upload, and clean Arduino code with

```
platformio run #compile arduino code
platformio run --target upload #compile and upload
platformio run --target clean #clean project 
```

Finally, once the code is running you can open a serial port connection with

```
platformio serialports monitor -p /dev/ttyUSB0 -b 115200 #a serial port monitor
```

Specifying the correct serial port for the Arduino is critical. Specify this in the treadmill.py file.

```
#serialStr = '/dev/tty.usbmodem618661' #teensy at work
#serialStr = '/dev/tty.usbmodem618661' #teensy?
#serialStr = '/dev/ttyUSB0' #hand soldered arduino micro (home debian)
#serialStr = '/dev/tty.usbserial-A50285BI' # hand soldered at work
serialStr = '/dev/ttyACM0' #uno
```

<a name="lowlevelinterrupts"></a>
### Low Level Interrupts

The Uno only comes with two pins (2 and 3) capable of low-level interrupts and more pins need to be broken out. We need two low level interrupts for the Rotary Encoder and a few more to quickly intercept TTL pulses of the FrameClock.

See [Pin-change interrupts][25] for information on exposing additional pins as low-level interrupts.

We have included a compiler directive `_expose_interrupts_` in treadmill.cpp that if activated will run code to expose additional interrupts. 

- If using platformio this is taken care of in the [env] section of platformio.ini
- If using the arduino IDE, `define _expose_interrupts_ = 1` must be included in [treadmill.cpp][4]

```
//Uncomment this line if running on an Arduino Uno and compiling with the arduino IDE
//#define _expose_interrupts_ 1
```

## Server Setup

###  Python

Download and install [Anaconda][1]. Anaconda is a [python][2] installation that will install many commonly used libraries. It is much easier to get started with Anaconda rather than a basic installation of Python.

###  Install required python libraries

Install additional required python libraries using the included requirements.txt file

`pip install -r requirements.txt`

Here is the requirements.txt file

```
eventlet>=0.18.4
Flask>=0.10.1
Flask-Markdown>=0.3
Flask-SocketIO>=1.0
platformio>=2.8.5
plotly>=1.9.6
pyserial>=3.0.1
```

## Running an experiment

At its core, an experiment is run on the Arduino using [treadmill.cpp][4]. We have provided two additional interfaces: a python interface and a web based interface.

###  Arduino interface

The Arduino program [treadmill.cpp][4] provides a simple serial interface to get and set parameters of a trial and to start and stop a trial. Once the program is uploaded to an Arduino, open your favorite serial port and start entering commands.

```
startTrial # start a trial
stopTrial # stop a trial
getState # 
settrial,[name],[value]
```

`settrial` takes the `name` and `value` of a trial parameter to set. The `name` needs to be one of: numPulse, numEpoch, epochDur, preDur, etc. These names match the 'Stimulus' parameters provided in the web interface. See the SetTrial() function in [treadmill.cpp][4] for all possible trial parameters.

Entering `getState` in a serial window and the Arduino will return the current values for all trial parameters. This is also a good way to find the names of trial parameters and then set them like `settrial,epochDur,5000`.

```
=== Arduino State ===
trialNumber=0
trialDur=1000
numEpoch=1
epochDur=1000
preDur=1000
postDur=1000
numPulse=3
pulseDur=1000
useMotor=1
motorDel=200
motorDur=200
motorSpeed=0
motorMaxSpeed=0
versionStr=20160322
=== Done ===
```

###  Python interface
You can  use iPython or any Python command interpreter to drive an experiment. You can also write your own python code to interface with the core python code in [treadmill.py][19].

Here is a short example of running an experiment in Python

```python
import treadmill
t = treadmill.treadmill() # create a treadmill object
t.startTrial() # start a new trial
t.stopTrial() # stop a trial
t.GetArduinoState() # get the current state with all trial parameters (see Arduino getstate below).
t.settrial('epochDur',5000) # set the value of 'epochDur' trial parameter to 5000 ms
t.startTrial() # start a new trial
```

The python interface and arduino interface share all trial parameter names.

###  Web interface

A web interface is provided as a [Flask][26] server in [treadmill_app.py][18]. Flask is a micro-framework that allows a web-server to be created and controlled all from within python.

Run the web interface with `python treadmill_app.py`. This will run a web server at `http://192.168.1.200:5000`. You can change the default address and port in [treadmill_app.py][18]

```
#this will run Flask on the machines local ip (use this if on a lan)
socketio.run(app, host='0.0.0.0', port=5010, use_reloader=True)
#this will run this on localhost, use this if using a single machine (no LAN needed)
socketio.run(app, host='', port=5010, use_reloader=True)
```

###  Rolling your own interface

You can roll your own interface by interfacing directly with the Arduino code in [treadmill.cpp][4], the python code in [treadmill.py][19], or the Flask server code in [treadmill_app.py][18].

## Links

Flask

- [flask-socketio][20]

- [flask-markdown][23]

- [eventlet][21]

Arduino

- [platormio][5]

- [platform io serial port monitor][24]

- [AccelStepper][16]

- [Rotary Encoder][17]


[1]: https://www.continuum.io/why-anaconda
[2]: http://www.python.org/

[3]:https://github.com/cudmore/treadmill/blob/master/requirements.txt
[4]: https://github.com/cudmore/treadmill/blob/master/arduino/src/treadmill.cpp
[5]: http://platformio.org/
[6]: http://docs.platformio.org/en/latest/quickstart.html#initialize-project

[7]: https://www.sparkfun.com/products/9238
[8]: https://www.sparkfun.com/products/12779
[9]: http://www.schmalzhaus.com/EasyDriver/
[10]: http://www.digikey.com/product-detail/en/600128CBL/600CS-ND/53504
[11]: http://sensing.honeywell.com/600%20series_005940-2-en_final_12sep12.pdf
[12]: https://www.sparkfun.com/products/9469
[13]: https://www.servocity.com/html/actoboticstm.html
[14]: https://www.sparkfun.com/actobotics
[15]: https://www.servocity.com/html/actoboticstm.html
[16]: http://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html
[17]: https://www.pjrc.com/teensy/td_libs_Encoder.html

[18]: https://github.com/cudmore/treadmill/blob/master/treadmill_app.py
[19]: https://github.com/cudmore/treadmill/blob/master/treadmill.py

[20]: https://flask-socketio.readthedocs.org/en/latest/
[21]: http://eventlet.net/
[22]: https://pythonhosted.org/pyserial/shortintro.html
[23]: https://pythonhosted.org/Flask-Markdown/
[24]: http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor
[25]: http://www.geertlangereis.nl/Electronics/Pin_Change_Interrupts/PinChange_en.html
[26]: http://flask.pocoo.org