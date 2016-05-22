#this needs to be run with sudo
# will stram raspberry camera
# see blog for installation of mjpg-streamer

echo ""
echo "`date +%y/%m/%d_%H:%M:%S`: start_stream" # 1>>/home/pi/stream.log

#20150322, add -bm for burst mode
#see: http://www.raspberrypi.org/forums/viewtopic.php?f=43&t=86997

if [ ! -d "/tmp/stream" ]; then
  mkdir /tmp/stream  
fi

#raspistill --nopreview -w 640 -h 480 -q 5 -o /tmp/stream/pic.jpg -tl 100 -t 9999999 -th 0:0:0 &  
raspistill --nopreview -w 640 -h 480 -q 5 -bm -o /tmp/stream/pic.jpg -tl 0 -t 9999999 -th 0:0:0 &  

#sleep 2

#-b will run in background and this script will return you to command line !!!

LD_LIBRARY_PATH=/usr/local/lib mjpg_streamer -b -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w /usr/local/www"


myip=$(hostname -I)
myip=$(echo -n $myip)

echo "View the stream in VLC with"
echo "http://$myip:9000/?action=stream"

#kill
#sudo killall raspistill # >>/home/pi/stream.log 2>>/home/pi/stream.log
#sudo killall mjpg_streamer # >>/home/pi/stream.log 2>>/home/pi/stream.log


echo ""