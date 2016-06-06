#20160606
#script to install triggercamera on Raspberry Pi running Raspian Jessie
# how do i add error checking to this?

    sudo apt-get -y install python-dev 
    sudo apt-get -y install python-eventlet
    sudo apt-get -y install python-pandas
 
    sudo pip install plotly

#should already be included with stock install of Raspian Jessie
    pip install pyserial
    pip install RPi.GPIO
    pip install picamera
    pip install ConfigParser

    pip install flask
    pip install flask-socketio

#to upload code to arduino

	pip install platformio
	
#uv4l for streaming video
#sudo apt-get -y install libav-tools 