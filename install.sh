#20160606
#script to install triggercamera on Raspberry Pi running Raspian Jessie
# how do i add error checking to this?

###
echo "    *****"
echo "    ***** Installing python-dev"
echo "    *****"
sudo apt-get -y install python-dev 
if [[ $? > 0 ]]
then
    echo "    ***** FAILED TO INSTALL 'python-dev' -->> EXITING"
    exit
fi

###
echo "    *****"
echo "    ***** Installing python-eventlet"
echo "    *****"
sudo apt-get -y install python-eventlet
if [[ $? > 0 ]]
then
    echo "    ***** FAILED TO INSTALL 'python-eventlet' -->> EXITING"
    exit
fi

###
echo "    *****"
echo "    ***** Installing python-pandas"
echo "    *****"
sudo apt-get -y install python-pandas
if [[ $? > 0 ]]
then
    echo "    ***** FAILED TO INSTALL 'python-pandas' -->> EXITING"
    exit
fi

 
sudo pip install plotly

#should already be included with stock install of Raspian Jessie
echo "    ***** Installing pyserial"
sudo pip install -q pyserial

echo "    ***** Installing RPi.GPIO"
sudo pip install -q RPi.GPIO

echo "    ***** Installing picamera"
sudo pip install -q picamera

echo "    ***** Installing ConfigParser"
sudo pip install -q ConfigParser

echo "    ***** Installing flask"
sudo pip install -q flask

echo "    ***** Installing flask-socketio"
sudo pip install -q flask-socketio

echo "    ***** Installing platformio"
sudo pip install -q platformio
	
#uv4l for streaming video
#sudo apt-get -y install libav-tools

echo " "
echo "Installation of required libraries for TriggerCamera is done."
echo "If there were no errors, proceed with 'sh setup'
