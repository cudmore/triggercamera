
{% filter markdown %}

### Web based experiment control


### Overview

This is a python server and web based javascript duo that allows an experiment to be run using an Arduino microcontroller.

It has been tested on both OS X and Debian Linux (Microsoft Windows is next).

### Interface

<IMG SRC="images/screenshot1.png" border="1">

The top section provides an interface to start/stop a trial and plots real-time feedback as the trial is running

The middle section provides an interface to set stimulus parameters for a trial and then upload these parameters to an Arduino. This section also provides a plot of what the trial will look like based on the set of parameters entered.


### Hardware

  - Stepper Motor, [sparkfun][11], ROB-09238, $15

  - Stepper motor driver, EasyDriver, [sparkfun][12], ROB-12779, $15. Main website for [EasyDriver][13]
  
  - Rotary encoder, [Honeywell-600-128-CBL][14], [.pdf spec sheet][15], $37
  
  - IR LED, 840-850 nm, [sparkfun][16] $1 each (960 nm IR LEDs do not work well with Pi Noir camera)

  - Actobotics at [ServoCity][17] and [sparkfun][18]. Give [ServoCity][17] a shot, their visual guides and project ideas are really helpful in desining components. This can be your one stop shop for all structural components including frames, rods, bearings, clamps, and motor mounts.
  
### Arduino libraries

Key is to use libraries that do not block your main event loop. These are 'non-blocking' and usually written in C.

  - [AccelStepper][19] library to control stepper motor
  
  - Rotary encoder library from [PJRC][20]
  
### Install Python using Anaconda

You can install python by downloading and installing Anaconda. The benefit compared to simply installing python is it comes pre-packaged with many common libraries.

Download [Anaconda][21]

### Install required python libraries

Install the required python libraries using the included requirements.txt file

  >> pip install -r requirements.txt
  
Here is the requirements.txt file
~~~
eventlet>=0.18.4
Flask>=0.10.1
Flask-Markdown>=0.3
Flask-SocketIO>=1.0
platformio>=2.8.5
plotly>=1.9.6
pyserial>=3.0.1
~~~

### [platformio][1] to compile and upload code to Arduino

Platformio is a python library so you should be good to go. Have a look at [xxx][xxx] to create a platformio.ini file for your specific arduino. Once platformio is configured, compile, upload, and clean with

~~~
platformio run
platformio run --target upload
platformio run --target clean

#a serial port monitor
platformio serialports monitor -p /dev/ttyUSB0 -b 115200 

~~~

### Serial Ports

~~~
# work osx
/dev/tty.usbmodem618661
/dev/tty.usbserial-A50285BI
~~~

### SimpleHTTPServer

Run a http server inside any folder using [SimpleHTTPServer][2]

~~~
python -m SimpleHTTPServer
~~~

### [Python serial][3]

~~~
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)  # open serial port
print(ser.name)         # check which port was really used
ser.write(b'hello')     # write a string
ser.close()             # close port
~~~

### Generating requirements.txt for other to install

Run 'pip freeze > requirements.txt' to create a full list of installed packages. Edit this list down to packages that go beyond standard Anaconda install.

~~~
Flask==0.10.1
Flask-Markdown==0.3
Flask-Misaka==0.4.1
Flask-SocketIO==1.0
eventlet==0.18.4

pyserial==3.0.1
ujson==1.33

plotly >1.9.4
~~~

### Serving fenced code blocks using python markdown library

To make Markdown parse fenced code blocks using '~~~', pass fenced_code as an extension when creating Mardown from Flask app
~~~
#see http://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html
Markdown(app, extensions=['fenced_code'])
~~~

Note: I could not get Misaka to work on my OSX install of Anaconda.
 
### Hardware

  - Stepper Motor, [sparkfun][11], ROB-09238, $15

  - Stepper motor driver, EasyDriver, [sparkfun][12], ROB-12779, $15. Main website for [EasyDriver][13]
  
  - Rotary encoder, [Honeywell-600-128-CBL][14], [.pdf spec sheet][15], $37
  
  - IR LED, 840-850 nm, [sparkfun][16] $1 each (960 nm IR LEDs do not work well with Pi Noir camera)

  - Actobotics at [ServoCity][17] and [sparkfun][18]. Give [ServoCity][17] a shot, their visual guides and project ideas are really helpful in desining components. This can be your one stop shop for all structural components including frames, rods, bearings, clamps, and motor mounts.
  
### Arduino libraries

Key is to use libraries that do not block your main event loop. These are 'non-blocking' and usually written in C.

  - [AccelStepper][19] library to control stepper motor
  
  - Rotary encoder library from [PJRC][20]
  
### Links

  - [flask-socketio][5]
  - [eventlet][6]
  - [platormio][1]
  - [simplehttpserver][2]
  - [pyserial][3]
  - [flask-misaka][4]
  - [flask-markdown][9] and [python markdown][10]
  - platform io [serial port monitor][7]
  - [AccelStepper][8] non blocking arduino library to control stepper motor
    
[1]: http://platformio.org/#!/
[2]: https://docs.python.org/2/library/simplehttpserver.html
[3]: https://pythonhosted.org/pyserial/shortintro.html
[4]: https://flask-misaka.readthedocs.org
[5]: https://flask-socketio.readthedocs.org/en/latest/
[6]: http://eventlet.net
[7]: http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor
[8]: http://www.airspayce.com/mikem/arduino/AccelStepper/index.html
[9]: https://pythonhosted.org/Flask-Markdown/
[10]: http://pythonhosted.org/Markdown

[11]: https://www.sparkfun.com/products/9238
[12]: https://www.sparkfun.com/products/12779
[13]: http://www.schmalzhaus.com/EasyDriver/

[14]: http://www.digikey.com/product-detail/en/600128CBL/600CS-ND/53504
[15]: http://sensing.honeywell.com/600%20series_005940-2-en_final_12sep12.pdf

[16]: https://www.sparkfun.com/products/9469

[17]: https://www.servocity.com/html/actoboticstm.html
[18]: https://www.sparkfun.com/actobotics

[19]: http://www.airspayce.com/mikem/arduino/AccelStepper/classAccelStepper.html

[20]: https://www.pjrc.com/teensy/td_libs_Encoder.html

[21]: https://www.continuum.io/downloads

{% endfilter %}
