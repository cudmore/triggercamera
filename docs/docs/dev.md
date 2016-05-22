#PlatformIO

    sudo pip install platformio #one time install
    
    platformio run --target upload
    
    platformio run --target clean
    
    platformio serialports monitor -p /dev/ttyACM0 -b 115200 #a serial port monitor
    
# mkDocs

    pip install mkdocs
    pip install mkdocs-cinder

    mkdocs serve
    mkdocs serve --dev-addr=0.0.0.0:8000 # serves built site on LAN IP
    
* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs help` - Print this help message.

## Deploy to github

mkdocs gh-deploy will use the gh-pages branch of repository specified in mkdocs.yml

	# this will deploy to github gh-pages specified in mkdocs.yml
	cd tiggercamera #should have mkdocs.yml file
	mkdocs build --clean
	mkdocs gh-deploy --clean 
	#site is then available at
	http://cudmore.github.io/triggercamera

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

# Install Raspbian

If you are Microsoft Windows based, have a look [here][mswindows] for a good install guide.

## Download image

As of May 21, 2016 the image was named `2016-05-10-raspbian-jessie`. [Download here][downloadraspian]

## Copy image to SD card

Follow an installation guide [here][installguide].

On Mac OS

    #Insert SD card and format as Fat32
	diskutil list # find the /dev/disk<n>, mine was /dev/disk3
	diskutil unmountDisk /dev/disk3 #unmount disk
	# copy .img file to disk
	sudo dd bs=1m if=/Users/cudmore/Downloads/2016-05-10-raspbian-jessie.img of=/dev/rdisk3

## First boot of the Pi

Connect Pi to a router with an ethernet cable and boot

Find IP address using router web interface, usually http://192.168.1.1

## Login via ssh

    ssh pi@192.168.1.15
    #password is raspberry
    
## Run configuration utility

    sudo raspi-config
  
 - 1 Expand Filesystem
 - 2 Change User Password
 - 3 Boot Options
    - B1 Console
 - 5 Internationalisation Options
    - I1 Change Local -> en_US.UTF-8 UTF-8
    - I2 Change Timezone -> US -> Eastern
    - I4 Change Wi-fi Country -> US United States
 - 6 Enable Camera
 - 9 Advanced Options
    - A2 Hostname -> [choose a name here, I chose pi3]
   
Selecting `3 Boot Options -> Console` is important. It seems Raspbian ships with X-Windows on by default.

## Update the system

    sudo apt-get update  #update database
    sudo apt-get upgrade #update userspace
    sudo rpi-update      #update firmware (requires reboot)
    sudo reboot          #reboot

## Apple File Protocol with open-source netatalk

Once netatalk is installed, the Raspberry will show up in the Mac Finder 'Shared' section

    sudo apt-get install netatalk
    
## Make the Pi send email with IP on boot

Create an executable python script to send en email with IP. An example [startup_mailer.py][startupmailer]

    mkdir code
    cd code
    wget https://github.com/cudmore/cudmore.github.io/raw/master/_site/downloads/startup_mailer.py
    chmod +x startup_mailer.py

Make sure the first line in the .py code is `#!/usr/bin/python`.

    #!/usr/bin/python

Set the email parameters in startup_mail.py

	to = 'robert.cudmore@gmail.com'
	gmail_user = 'cudmore.raspberry@gmail.com'
	gmail_password = 'ENTER_YOUR_PASSWORD_HERE'

Run crontab as root and append one line `@reboot (sleep 10; /home/pi/code/startup_mailer.py)`

    sudo crontab -e

Add this to end (sleep 5 does not work!!!!)

    @reboot (sleep 10; /home/pi/code/startup_mailer.py)

Now, when pi boots it will send an email with it's ip. Try it with

    sudo reboot

[downloadraspian]: https://www.raspberrypi.org/downloads/
[installguide]: https://www.raspberrypi.org/documentation/installation/installing-images/README.md
[mswindows]: http://www.circuitbasics.com/raspberry-pi-basics-setup-without-monitor-keyboard-headless-mode/
[startupmailer]: https://github.com/cudmore/cudmore.github.io/blob/master/_site/downloads/startup_mailer.py