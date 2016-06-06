#see: http://www.linux-projects.org/modules/sections/index.php?op=viewarticle&artid=14

#generate keys with
#openssl genrsa -out selfsign.key 2048 && openssl req -new -x509 -key selfsign.key -out selfsign.crt -sha256

#then run with

#mjpeg
#uv4l --driver raspicam --auto-video_nr --encoding mjpeg --width 640 --height 480 --enable-server on --server-option --ssl-private-key-file /home/pi/Sites/triggercamera/selfsign.key --server-option --ssl-certificate-file /home/pi/Sites/triggercamera/selfsign.crt 

#h264
uv4l --driver raspicam --auto-video_nr --encoding h264 --width 640 --height 480 --enable-server on

#uv4l --driver raspicam --auto-video_nr --encoding mjpeg --width 640 --height 480 --enable-server on

