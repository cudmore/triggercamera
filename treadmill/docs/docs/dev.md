## Development

These are development notes taken during the development of the Treadmill.

### mkDocs

This documentation is written in markdown and a static site is generated with [mkDocs][25] using the [Cinder][26] theme. Previously I have used Jekyll which is amazing. Going with mkDocs to see if a simple site is acceptable.

When writing markdown, serve a mkDocs site locally with

```
cd docs/
mkdocs serve --dev-addr=0.0.0.0:8000 # serves built site on LAN IP
mkdocs serve # serves built site on localhost at 127.0.0.1:8000

mkdocs build #generates the site into docs/site/
```

### Deploy to Github gh-pages

Deploy to github gh-pages by follow mkDocs [deployment instructions][27].

`mkdocs gh-deploy` will use the gh-pages branch of repository specified in `mkdocs.yml`

    # this will deploy to github gh-pages specified in mkdocs.yml
    cd docs #should have mkdocs.yml file
    mkdocs build --clean
    mkdocs gh-deploy --clean 
    #site is then available at
    http://cudmore.github.io/treadmill

I am doing this on OSX. Not doing this on Debian because I do not have git/github properly configured.


### Tweak Cinder

Along the way I have actually contributed to **Cinder**, the mkDocs template that makes this site. See [here](https://github.com/chrissimpkins/cinder/pull/11).

Use 'pip show mkdocs' to figure out where your cinder files are

    pip show mkdocs
    /home/cudmore/anaconda2/lib/python2.7/site-packages

### Generate a single PDF from mkDocs site

Use [mkdocs-pandoc][2] to convert the mkdocs site into a single pdf. This creates a table of contents and appends all .md files using [pandoc][3] as a backend.

```
cd docs
mkdocs2pandoc > mydocs.pd
pandoc --toc -f markdown+grid_tables+table_captions -o mydocs.pdf mydocs.pd   # Generate PDF
pandoc --toc -f markdown+grid_tables -t epub -o mydocs.epub mydocs.pd         # Generate EPUB
```

I found it easy to do this on OSX using the pandoc installer. I did not get this working on Debian.

### Platformio

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

#[env:pro16MHzatmega328]
#platform = atmelavr
#framework = arduino
#board = pro16MHzatmega328

#[env:nodemcuv2]
#platform = espressif
#framework = arduino
#board = nodemcuv2
#upload_port = /dev/ttyUSB0
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

### 5V Relay

A relay allows a 3.5 or 5 V DIO pin to turn a higher voltage switch on and off. For example, you use a 5V relay to turn a 12V line on and off.

How to wire a 5V relay is here

http://www.codeguru.com/IoT/understanding-relays-in-iot-development.html

[1]: http://robertcudmore.org
[2]: https://github.com/jgrassler/mkdocs-pandoc
[3]: http://pandoc.org
[4]: http://www.mkdocs.org/user-guide/deploying-your-docs/
[25]: http://www.mkdocs.org
[26]: http://sourcefoundry.org/cinder/
[27]: https://mkdocs.readthedocs.org/en/stable/user-guide/deploying-your-docs/