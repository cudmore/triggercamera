#(1) need to use eventlet, otherwise .run() defaults to gevent() which is SLOW
#(2) monkey_path() wraps some functions to call eventlet equivalents
#   in particule time.sleep() is redirected to coresponding eventlet() call
#
from flask import Flask, abort, render_template, send_file, request
from flask.ext.socketio import SocketIO, emit
from flaskext.markdown import Markdown

import random # testing
import os, time, random
from datetime import datetime
from threading import Thread
import eventlet
import json

from treadmill import treadmill
from treadmillAnalysis import treadmillAnalysis
from plotly_plot import myplotlyplot

from settings import APP_ROOT

#see: https://github.com/miguelgrinberg/Flask-SocketIO/issues/192
eventlet.monkey_patch()

#eventlet.debug.hub_prevent_multiple_readers(False)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug = True
app.config['DATA_FOLDER'] = 'data/'

Markdown(app, extensions=['fenced_code'])

#socketio = SocketIO(app)
socketio = SocketIO(app, async_mode='eventlet')

#namespace = '/test'
namespace = ''

thread = None #second thread used by background_thread()
ser = None

#b = bSerial.bSerial(socketio)
mytreadmill = None
myanalysis = None

def background_thread():
	"""Example of how to send server generated events to clients."""
	while True:
		time.sleep(.7)
		response = MakeServerResponse()		

		jsonResponse = json.dumps(response)
		#print 'sending:', jsonResponse
		socketio.emit('serverUpdate', jsonResponse, namespace=namespace)
		
def MakeServerResponse():
	#print 'MakeServerResponse()'
	now = datetime.now()
	dateStr = now.strftime("%m/%d/%y")
	timeStr = now.strftime("%H:%M:%S.%f")
	
	response = {}
	response['currentdate'] = dateStr
	response['currenttime'] = timeStr

	response['savepath'] = mytreadmill.savepath
	response['animalID'] = mytreadmill.animalID

	response['filePath'] = mytreadmill.trial['filePath']
	response['fileName'] = mytreadmill.trial['fileName']

	response['trialRunning'] = mytreadmill.trialRunning
	response['trialNumber'] = mytreadmill.trial['trialNumber']
	response['trialDur'] = mytreadmill.trial['trialDur']

	response['epochNumber'] = mytreadmill.trial['epochNumber']
	response['numEpoch'] = mytreadmill.trial['numEpoch']

	response['useMotor'] = mytreadmill.trial['useMotor']
	response['motorDel'] = mytreadmill.trial['motorDel']
	response['motorDur'] = mytreadmill.trial['motorDur']

	return response
	
@app.route('/')
def index():
	global thread
	if thread is None:
		print('starting background thread')
		thread = Thread(target=background_thread)
		thread.daemon  = True; #as a daemon the thread will stop when *this stops
		thread.start()
	theRet = render_template('index.html', treadmill=mytreadmill)
	return theRet

@app.route('/form2')
def form2():
	return render_template('form_sandbox.html')

'''
@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = '/Users/vivek/Desktop'

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)
'''

#from: http://stackoverflow.com/questions/23718236/python-flask-browsing-through-directory-with-files
@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):

	print '\n'
	print 'req_path:', req_path
	
	# Joining the base and the requested path
	abs_path = os.path.join(APP_ROOT, req_path)

	print 'abs_path:', abs_path

	# Return 404 if path doesn't exist
	if not os.path.exists(abs_path):
		return abort(404)

	# Check if path is a file and serve
	if os.path.isfile(abs_path):
		return send_file(abs_path)

	# Show directory contents
	if os.path.isdir(abs_path):
		print 'IS DIRECTORY:', abs_path
	files = os.listdir(abs_path)
	return render_template('files.html', path=req_path.replace('data/','') + '/', files=files)

@app.route('/analysis')
def analysis():
	#list = myAnalysis.getlist()
	#return render_template('analysis.html', list=list)
	myAnalysis.builddb('')
	return render_template('analysis2.html')
	
@app.route('/help')
def help():
	return render_template('help.md')
	
@app.route('/p5')
def index_highchart():
	return render_template('p5.html')

@app.route('/grafica')
def index_grafica():
	return render_template('grafica.html')

'''
@app.route('/plotly')
def plotly():
	file = 'data/20160306_211227_t4_d.txt'
	print 'file=', file
	plotheader, plothtml = myplotlyplot('data/' + file)
	print 'plothtml=', plothtml
	plothtml = os.path.basename(plothtml)
	return render_template(plothtml)
'''

@socketio.on('connectArduino', namespace=namespace) #
def connectArduino(message):
	emit('my response', {'data': message['data']})
	print 'connectArduino', message['data']

@socketio.on('startarduinoButtonID', namespace=namespace) #
def startarduinoButton(message):
	print 'startarduinoButtonID'
	mytreadmill.startTrial()
	
@socketio.on('stoparduinoButtonID', namespace=namespace) #
def stoparduinoButtonID(message):
	print 'stoparduinoButtonID'
	mytreadmill.stopTrial()
	
@socketio.on('printArduinoStateID', namespace=namespace) #
def printArduinoStateID(message):
	mytreadmill.GetArduinoState()

@socketio.on('emptySerialID', namespace=namespace) #
def printArduinoStateID(message):
	mytreadmill.emptySerial()

@socketio.on('checkserialportID', namespace=namespace) #
def checkserialportID(message):
	exists, str = mytreadmill.checkserialport()
	if exists:
		emit('serialdata', {'data': "OK: " + str})
	else:
		emit('serialdata', {'data': "ERROR: " + str})

@socketio.on('setSerialPortID', namespace=namespace) #
def setSerialPort(message):
	portStr = message['data']
	ok = mytreadmill.setserialport(portStr)
	if ok:
		emit('serialdata', {'data': "OK: " + portStr})
	else:
		emit('serialdata', {'data': "ERROR: " + portStr})

@socketio.on('arduinoVersionID', namespace=namespace) #
def arduinoVersionID(message):
	mytreadmill.checkarduinoversion()

@socketio.on('my event', namespace=namespace) #responds to echo
def test_message(message):
	emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace=namespace)
def test_message(message):
	emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace=namespace)
def test_connect():
	emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
	print('*** treadmill_app -- Client disconnected')

@socketio.on('trialform', namespace=namespace)
def trialform(message):
	'''message is trailFormDict from treadmill object'''
	print '\n=== treadmill_app.trialform:', message
	preDur = message['preDur']
	postDur = message['postDur']

	numEpoch = message['numEpoch']
	epochDur = message['epochDur']

	numPulse = message['numPulse']
	pulseDur = message['pulseDur']
	useMotor = message['useMotor'] #{motorOn, motorLocked, motorFree}
	motorDel = message['motorDel']
	motorDur = message['motorDur']
	motorSpeed = message['motorSpeed']
	#
	
	emit('serialdata', {'data': "=== Trial Form ==="})
	
	mytreadmill.settrial('preDur', preDur)
	time.sleep(0.01)
	mytreadmill.settrial('postDur', postDur)
	time.sleep(0.01)

	mytreadmill.settrial('numEpoch', numEpoch)
	time.sleep(0.01)
	mytreadmill.settrial('epochDur', epochDur)
	time.sleep(0.01)

	mytreadmill.settrial('numPulse', numPulse)
	time.sleep(0.01)
	mytreadmill.settrial('pulseDur', pulseDur)
	time.sleep(0.01)
	#mytreadmill.settrial('useMotor', useMotor)
	time.sleep(0.01)
	mytreadmill.settrial('motorDel', motorDel)
	time.sleep(0.01)
	mytreadmill.settrial('motorDur', motorDur)
	time.sleep(0.01)
	mytreadmill.settrial('motorSpeed', motorSpeed)
	time.sleep(0.01)
	
	mytreadmill.settrial('useMotor', useMotor)
	time.sleep(0.01)

	mytreadmill.updatetrial() #update total dur
	
	mytreadmill.emptySerial()
	
	print 'trialform() useMotor=', useMotor
	
	trialDiv = myAnalysis.plottrialparams(mytreadmill.trial)
	emit('trialPlotDiv', {'data': trialDiv})

	emit('serialdata', {'data': "=== Trial Form Done ==="})

@socketio.on('animalform', namespace=namespace)
def animalform(message):
	print 'animalform:', message
	animalID = message['animalID']
	mytreadmill.animalID = animalID
	#mytreadmill.settrial('dur', dur)
	emit('my response', {'data': "animal id is now '" + animalID + "'"})


@socketio.on('plotTrialButtonID', namespace=namespace)
def plotTrialButton(message):
	filePath = message['data']
	print 'plotTrialButton() filename:' + filePath
	divStr = myplotlyplot(filePath,'div')
	emit('lastTrialPlot', {'plotDiv': divStr})

@socketio.on('plotTrialHeaderID', namespace=namespace)
def plotTrialHeader(message):
	filename = message['data']
	print 'plotTrialHeader() filename:' + filename
	headerStr = myAnalysis.loadheader(filename)
	emit('headerDiv', {'headerStr': headerStr})

@socketio.on('filterTrial', namespace=namespace)
def filterTrial(message):
	filename = myAnalysis.builddb(message['data'])
	emit('refreshList', {'data': filename})


if __name__ == '__main__':
	try:
	
		#print 'initializing treadmill'
		mytreadmill = treadmill()
		dataRoot = os.path.join(APP_ROOT, "data") + '/'
		mytreadmill.setsavepath(dataRoot)
		mytreadmill.bAttachSocket(socketio)
		
		#print 'initializing treadmillAnalysis'
		myAnalysis = treadmillAnalysis()
		myAnalysis.assignfolder(dataRoot)
		
		print('starting server')
		socketio.run(app, host='0.0.0.0', port=5010, use_reloader=True)
		print('finished')
	except:
		print '...exiting'
		raise