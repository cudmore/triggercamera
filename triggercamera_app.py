# Author: Robert H Cudmore
# Web: http://robertcudmore.org
# Date: 20151205
#Purpose: Run a Flask webserver to provide a REST interface to VideoServer.py
#

'''
API
===
http://server/

http://server/startarm
http://server/stoparm

http://server/startvideo
http://server/stopvideo

http://server/timelapseon
http://server/timelapseoff

'''
import time, datetime, platform
import pprint #to print class members
from threading import Thread
from flask import Flask, jsonify, send_file, redirect, render_template
from flask.ext.socketio import SocketIO, emit
import eventlet
#import json

import triggercamera
import triggercamera_analysis

#see: https://github.com/miguelgrinberg/Flask-SocketIO/issues/192
eventlet.monkey_patch()

print 'triggercamera_app starting server at:', time.strftime("%m/%d/%y"), time.strftime("%H:%M:%S")

app = Flask(__name__, template_folder='triggercamera_app/templates', static_folder='triggercamera_app/static')

socketio = SocketIO(app, async_mode='eventlet')

print 'instantiating triggercamera.TriggerCamera()'
v=triggercamera.TriggerCamera()
v.ArmTrigger()
#v.startArm()

tca = triggercamera_analysis.triggercamera_analysis()

namespace = ''

thread = None #second thread used by background_thread()

def background_thread():
	"""Example of how to send server generated events to clients."""
	while True:
		time.sleep(.7)
		response = genericresponse()		

		socketio.emit('serverUpdate', response, namespace=namespace)
		
def genericresponse():
    dateStr = time.strftime("%m/%d/%y")
    timeStr = time.strftime("%H:%M:%S")

    resp = {}
    resp['date'] = dateStr
    resp['time'] = timeStr
    resp['isArmed'] = v.isArmed
    resp['videoStarted'] = v.videoStarted

    resp['scanImageFrame'] = v.scanImageFrame
    resp['logFilePath'] = v.logFilePath
    
    resp['fps'] = v.config['camera']['fps']
	
    return resp
    
@socketio.on('plotTrialButtonID', namespace=namespace)
def plotTrialButton(message):
	logFilePath = v.logFilePath #message['data']
	print 'plotTrialButton() logFilePath:', logFilePath
	divStr = tca.plotfile(logFilePath)
	emit('lastTrialDiv', {'plotDiv': divStr})

@app.route('/startarm', methods=['GET'])
def startArm():
    v.startArm()
    return genericresponse()
    
@app.route('/stoparm', methods=['GET'])
def stopArm():
    v.stopArm()
    return genericresponse()
    
@app.route('/startvideo', methods=['GET'])
def startVideo():
    v.startVideo()
    return genericresponse()
    
@app.route('/stopvideo', methods=['GET'])
def stopVideo():
    v.stopVideo()
    return genericresponse()
    
@app.route('/timelapseon', methods=['GET'])
def timelapseon():
    v.doTimelapse = 1
    return genericresponse()
    
@app.route('/timelapseoff', methods=['GET'])
def timelapseoff():
    v.doTimelapse = 0
    return genericresponse()
    
@app.route('/system', methods=['GET'])
def system():
    return genericresponse()

@app.route('/loadconfig', methods=['GET'])
def loadconfig():
    v.ParseConfigFile()
    return genericresponse()

#redirect lastimage to address with v.lastimage filename
@app.route('/lastimage', methods=['GET'])
def lastimage():
    if v.lastimage:
        return redirect('/lastimage/' + v.lastimage)
    else:
        return 'no last image' + '<BR>' + genericresponse()

@app.route('/lastimage/<filename>')
def send_lastimage(filename):
    if '..' in filename or filename.startswith('/'):
        return 'please don\'t be nasty'
    else:
        return send_file(v.savepath + filename)
        
@app.route('/help', methods=['GET'])
def help():
    ret = 'REST Interface' + '<BR>'
    ret += '--------------' + '<BR>'
    ret += 'startarm' + '<BR>'
    ret += 'stoparm' + '<BR>'
    ret += 'startvideo' + '<BR>'
    ret += 'stopvideo' + '<BR>'
    ret += 'timelapseon' + '<BR>'
    ret += 'timelapseoff' + '<BR>'
    ret += 'lastimage' + '<BR>'
    ret += 'loadconfig' + '<BR>'
    return ret

#home page
@app.route('/', methods=['GET'])
def get_index():
    global thread
    if thread is None:
        print('starting background thread')
        thread = Thread(target=background_thread)
        thread.daemon  = True; #as a daemon the thread will stop when *this stops
        thread.start()
    #resp = genericresponse()
    return render_template('index.html') #, resp=resp)

#start the app/webserver
if __name__ == "__main__":
    try:
        #app.run(host='0.0.0.0', port=5010, use_reloader=True, debug=True)
        socketio.run(app, host='0.0.0.0', port=5010, use_reloader=False)
    except:
        print 'triggercamera_app EXITING AND AT LAST LINE'
        raise

