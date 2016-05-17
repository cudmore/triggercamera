echo ""
echo "`date +%y/%m/%d_%H:%M:%S`: stop_stream" # 1>>/home/pi/stream.log

sudo killall raspistill # >>/home/pi/stream.log 2>>/home/pi/stream.log
sudo killall mjpg_streamer # >>/home/pi/stream.log 2>>/home/pi/stream.log

