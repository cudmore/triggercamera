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

print 'triggercamera_app starting import of libraries'

import time, datetime, platform, math, re
#import logging
from threading import Thread
from flask import Flask, jsonify, send_file, redirect, render_template
from flask.ext.socketio import SocketIO, emit
import eventlet
import subprocess # to get ip address
#import json

print '\timport triggercamera and triggercamera_analysis (please wait)'
import triggercamera
import triggercamera_analysis

#see: https://github.com/miguelgrinberg/Flask-SocketIO/issues/192
eventlet.monkey_patch()

print '\tstarting Flask server at:', time.strftime("%m/%d/%y"), time.strftime("%H:%M:%S")

app = Flask(__name__, template_folder='triggercamera_app/templates', static_folder='triggercamera_app/static')

socketio = SocketIO(app, async_mode='eventlet')

print '\tinstantiating triggercamera.TriggerCamera()'
v=triggercamera.TriggerCamera()
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
	resp['streamIsRunning'] = v.streamIsRunning
	
	resp['videoStarted'] = v.videoStarted
	if v.videoStarted and v.trialStartTime>0:
		resp['elapsedTime'] = math.floor(time.time() - v.trialStartTime)
	else:
		resp['elapsedTime'] = ''

	resp['numFrames'] = v.numFrames
	resp['trialNumber'] = v.trialNumber
	resp['logFilePath'] = v.logFilePath
	resp['sessionID'] = v.sessionID
	
	resp['led1On'] = v.led1On
	resp['led2On'] = v.led2On

	resp['fps'] = v.config['camera']['fps']
	resp['resolution'] = v.config['camera']['resolution']
	resp['bufferSeconds'] = v.config['camera']['bufferSeconds']
	
	
	resp['useTwoTriggerPins'] = v.config['triggers']['useTwoTriggerPins']
	resp['triggerPin'] = v.config['triggers']['triggerpin']
	resp['framePin'] = v.config['triggers']['framepin']

	resp['serialPort'] = v.config['serial']['port']

	resp['gbSize'] = v.gbSize
	resp['gbRemaining'] = v.gbRemaining

	resp['cpuTemperature'] = v.cpuTemperature
	
	resp['simulatescope'] = v.config['simulatescope']['on']
	
	return resp
	
@socketio.on('sessionform', namespace=namespace)
def sessionform(message):
	print 'sessionform:', message
	sessionID = message['sessionID']
	if len(sessionID)<10 and (sessionID=='' or re.match('^\w+$',sessionID)):
		v.sessionID = sessionID
	response = genericresponse()		
	socketio.emit('serverUpdate', response, namespace=namespace)

@socketio.on('plotTrialButtonID', namespace=namespace)
def plotTrialButton(message):
	logFilePath = v.logFilePath #message['data']
	if logFilePath:
		#print 'plotTrialButton() logFilePath:', logFilePath
		divStr = tca.plotfile(logFilePath,'div')
		emit('lastTrialDiv', {'plotDiv': divStr})

@socketio.on('plotAnalysisTrialButtonID', namespace=namespace)
def plotAnalysisTrialButtonID(message):
	filePath = message['data']
	#print 'plotTrialButton2() filename:' + filePath
	divStr = tca.plotfile(filePath,'div', divWidth=600, divHeight=300)
	emit('plotTrialDiv', {'plotDiv': divStr})


@socketio.on('startArmButtonID', namespace=namespace)
def startArmButton(message):
	v.startArm()
	response = genericresponse()		
	socketio.emit('serverUpdate', response, namespace=namespace)

@socketio.on('stopArmButtonID', namespace=namespace)
def stopArmButton(message):
	v.stopArm()
	response = genericresponse()		
	socketio.emit('serverUpdate', response, namespace=namespace)

@socketio.on('startStreamButtonID', namespace=namespace)
def startStreamButton(message):
	v.startVideoStream()
	response = genericresponse()		
	#socketio.emit('serverUpdate', response, namespace=namespace)
	socketio.emit('refreshvideostream', response, namespace=namespace)

@socketio.on('stopStreamButtonID', namespace=namespace)
def stopStreamButton(message):
	v.stopVideoStream()
	response = genericresponse()		
	socketio.emit('serverUpdate', response, namespace=namespace)
	#socketio.emit('refreshvideostream', response, namespace=namespace)

@socketio.on('ledButtonID', namespace=namespace)
def ledButton(msg):
	led = msg['led']
	on = msg['on']
	print 'ledButton()', led, on
	if led == 1:
		v.led1On = on
	elif led == 2:
		v.led2On = on
	response = genericresponse()		
	socketio.emit('serverUpdate', response, namespace=namespace)

@socketio.on('runSimulationButtonID', namespace=namespace)
def runSimulationButton(msg):
	v.sendSerial('start')
	
@socketio.on('reloadConfig', namespace=namespace)
def reloadConfig(msg):
	v.ParseConfigFile()

@socketio.on('simulateCheckbox', namespace=namespace)
def simulateCheckbox(msg):
	isOn = v.config['simulatescope']['on']
	isOn = not isOn
	v.config['simulatescope']['on'] = isOn
	print 'simulateCheckbox=', isOn
	
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
@app.route('/analysis', methods=['GET'])
def analysis():
	tca.builddb('')
	return render_template('analysis.html') #, resp=resp)

@app.route('/', methods=['GET'])
def get_index():
	global thread
	if thread is None:
		print('triggercamera_app:route / is starting background thread')
		thread = Thread(target=background_thread)
		thread.daemon  = True; #as a daemon the thread will stop when *this stops
		thread.start()
	#resp = genericresponse()
	return render_template('index.html') #, resp=resp)

def whatismyip():
	arg='ip route list'
	p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
	data = p.communicate()
	split_data = data[0].split()
	ipaddr = split_data[split_data.index('src')+1]
	return ipaddr
	
#start the app/webserver
if __name__ == "__main__":
	try:
		print '\ttriggercamera_app::__main__'
		#app.run(host='0.0.0.0', port=5010, use_reloader=True, debug=True)
		# this works for lan ip but shows 0.0.0.0 in std out
		#socketio.run(app, host='0.0.0.0', port=5010, use_reloader=False)
		socketio.run(app, host=whatismyip(), port=5010, use_reloader=False)
		print 'xxx here'
	except:
		print 'triggercamera_app EXITING AND AT LAST LINE'
		raise

