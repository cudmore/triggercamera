#create symbolic link on cudmore hom-hack
#ln -s /Volumes/fourt/homevideo/ homevideo

#convert directory of .jpg to .mp4
#ffmpeg -f image2 -pattern_type glob -r 10 -i '*.jpg' -vcodec libx264 -vf scale=1280x960 -b:a 192k out.mp4

import os
import logging
import paramiko
import socket
import time
import picamera

username='cudmore'
password='poetry7d'
hostname = '192.168.1.10'
port=22
source= './tst.jpg' 
destination ='tst.jpg'

savepath = '/home/pi/video/'
remotepath = './'

camera = None

def timestamp(): #use this to generate .avi
    return time.strftime('%Y%m%d') + '_' + time.strftime('%H%M%S')

##
#logger = logging.getLogger(__name__)
logger = logging.getLogger('')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(savepath + timestamp() + '.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#log to console, stdout
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
##

def initcamera():
    global camera
    camera = picamera.PiCamera()
    camera.resolution = (2592, 1944)
    #camera.led = 0
    camera.start_preview()

def captureimage(name):
    logger.info('captureimage() is capturing image ' + name)
    camera.capture(name, quality=100)

def transferfile(path, name):
    ssh = None
    sftp = None
    try:
        logger.info('transferfile() is transferring ' + path + name)
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        logger.info('establishing connection to ' + hostname)
        
        #ssh.connect(hostname, username, password)
        
        #sftp = ssh.open_sftp()
        
        t = paramiko.Transport((hostname, port)) 
        t.connect(username=username,password=password)
        sftp = paramiko.SFTPClient.from_transport(t)

        srcfile = path + name
        dstfile = 'homevideo/' + name
        logger.info('transferring: ' + 'src=' + srcfile + ' dst=' + dstfile)
        sftp.put(srcfile,dstfile)

        #close connection
        sftp.close()
        ssh.close()
        
        #delete file
        logger.info('deleting file: ' + path + name)
        os.remove(path+name)
        
    except paramiko.SSHException, e:
        logger.error('Password is invalid', exc_info=True)
    except paramiko.AuthenticationException:
        logger.error('Authentication failed for some reason', exc_info=True)
    except socket.error, e:
        logger.error('Socket connection failed', exc_info=True)
    except Exception, e:
        logger.error('transferfile() except taken', exc_info=True)
    except (KeyboardInterrupt):
        logger.info('user cancelled transferfile() with ctrl-c at ' + timestamp())
        raise
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()

def run():
    #transferfile()
    imageinterval = 60 #seconds
    lasttime = 0
    
    i = 0
    try:
        #while i < 2:
        while True:
            thistime = time.time()
            thistimestamp = timestamp()
            if thistime > (lasttime + imageinterval):
                lasttime = thistime
            
                #snap a new image
                newimagename = thistimestamp + '.jpg'
                newimagepath = savepath + newimagename
                captureimage(newimagepath)
            
                #transfer to home desktop    
                #transferfile(savepath, newimagename)
            
                logger.info('finished with image ' + str(i))
                
                i = i + 1
            time.sleep(0.5)
            
    except (KeyboardInterrupt):
        logger.info('user cancelled run() with ctrl-c at ' + timestamp())
        raise
    logger.info('run() is finished at ' + timestamp())

#############################################################################     
if __name__ == "__main__":

    logger.info('Start at ' + timestamp())
    
    #init camera
    initcamera()
    
    run()
    
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
        
    