#20160522

import plotly
print 'plotly.__version__=', plotly.__version__  # version >1.9.4 required
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import os.path
import glob
import ntpath #this shuod get paths on windows?

class triggercamera_analysis():
	def __init__(self):
		print 'construct triggercameraAnalysis'
		self.folder = '/home/pi/video/'
		self.list = ''
		self.dbfile = ''

	def readfileheader(self, filePath):
		with open(filePath, 'r') as f:
		    first_line = f.readline()
    		return first_line
    		
	'''
	fps=30,width=640,height=480,numFrames=300
	date,time,seconds,event,frameNumber
	20160604,165218,1465073538.39,startVideo,
	20160604,165218,1465073538.39,scanImageFrame,1
	20160604,165218,1465073538.42,scanImageFrame,2
	20160604,165218,1465073538.45,scanImageFrame,3
	20160604,165218,1465073538.48,scanImageFrame,4
	20160604,165218,1465073538.51,scanImageFrame,5
	'''
	
	def builddb(self, sessionStr):
		'''build a db'''
		'''this is assuming the data format for ALL files in folder are same'''
		'''todo: add a file version to header and check if this is the case'''
		
		#open db file
		writefile = 'triggercamera_db.csv'
		if sessionStr:
			writefile = 'triggercamera_db_' + sessionStr + '.csv'
		#dbFile = self.folder + writefile
		dbFile = '/home/pi/Sites/triggercamera/triggercamera_app/static/' + writefile
		print 'writing dbfile:', dbFile, 'sessionStr:', sessionStr
		dbID = open(dbFile, 'w')
		
		numFiles = 0
		firstfile = 1
		rowIdx = 0
		for root, subdirs, files in os.walk(self.folder):
			#print 'root:', root
			#print '\tsubdirs:', subdirs
			#print '\t\tfiles:', files
			#print 'root:', root
			for filename in files:
				if filename.endswith('.txt'):
					sessionName = ntpath.basename(root) # session name is name of enclosing folder
					if sessionStr and not (sessionName.find(sessionStr) >= 0):
						#print '      rejecting:', sessionName
						continue
					if sessionName == '.AppleDouble':
						continue
					#else:
					#	print '   accepting', sessionName
					file_path = os.path.join(root, filename)
					with open(file_path, 'r') as f:
						numFiles += 1
						#header of each file is:
						#date=xxx,time=yyy,fps=30,width=640,height=480,numFrames=300,ardFrames=0
						header = f.readline()
						#
						#print header
						if firstfile:
							dbID.write('Idx' + ',')
							dbID.write('Session' + ',')
							for nv in header.split(','):
								#print nv
								if nv.find('=')>=0:									
									k, v = nv.split('=')
									dbID.write(k + ',')
							#dbID.write('file_path' + ',')
							dbID.write('file_path')
							dbID.write('\n')
							firstfile = 0
						#
						#write values
						dbID.write(str(rowIdx) + ',') #Idx
						dbID.write(sessionName + ',') #sessionName
						for nv in header.split(','):
							#print nv
							if nv.find('=')>=0:									
								k, v = nv.split('=')
								v = v.rstrip()
								#print 'k=',"'",k,"'","'",v,"'"
								dbID.write(v + ',')
						#dbID.write(file_path + ',')						
						dbID.write(file_path)						
						dbID.write('\n')						
						rowIdx += 1
		dbID.close()
		print 'db has', numFiles
		return writefile

	def plotfile(self,filePath,output_type, divWidth=500, divHeight=200):
		'''
		output_type: ('file', 'div')
		'''
		
		#date,time,seconds,event,frameNumber
		df = pd.read_csv(filePath, skiprows=1)
		
		sif = df.loc[df['event'] == 'numFrames']
		
		diff = np.diff(sif['seconds'].astype('float'))
		diff *= 1000 #seconds to ms
		frames = df['frameNumber']

		trace0 = go.Scatter(
			x = frames,
			y = diff,
			mode = 'lines+markers',
			name = 'rasp'
		)

		#
		#arduino
		ard_frame = df.loc[df['event'] == 'ardFrame']
		ard_diff = np.diff(ard_frame['seconds'].astype('float'))
		ard_frame = ard_frame['frameNumber']
		
		trace1 = go.Scatter(
			x = ard_frame,
			y = ard_diff,
			mode = 'lines+markers',
			name = 'ard'
		)
		
		layout = {
			'title': '',
			'xaxis': {
				#'range': [0, totalDur],
				'autotick':True,
				'title':'Frames',
			},
			'yaxis': {
				#'range': [0, 5],
				#'showgrid': False,
				#'ticks': '',
				#'showticklabels': False,
				'title':'Interval (ms)',
			},
			'width': divWidth,
			'height': divHeight,
			'margin': {
				'l':50,
				'r':20,
				'b':50,
				't':20,
				'pad':5
			},
			#'shapes': myShapes,
		}
		
		data = [trace0, trace1]
		
		fig = {
			'data': data,
			'layout': layout,
		}
		#output_type = 'file'
		fileordiv = plotly.offline.plot(fig, show_link=False, filename='triggercamera_app/templates/lastplot.html', output_type=output_type, auto_open=False)

		return fileordiv

	'''
	millis,absmillis,event,frame
	416161,0,trialStart,
	416161,0,frame,0
	416191,30,frame,1
	416221,60,frame,2
	416251,90,frame,3
	416281,120,frame,4
	416311,150,frame,5
	'''
	def plotarduinofile(self, filePath):
		df = pd.read_csv(filePath)
		frame = df.loc[df['event'] == 'frame']
		diff = np.diff(frame['absmillis'].astype('float'))
		frames = df['frame']
	
		layout = {
			'title': '',
			'xaxis': {
				#'range': [0, totalDur],
				'autotick':True,
				'title':'Frames',
			},
			'yaxis': {
				#'range': [0, 5],
				#'showgrid': False,
				#'ticks': '',
				#'showticklabels': False,
				'title':'Interval (ms)',
			},
			'width': 500,
			'height': 200,
			'margin': {
				'l':50,
				'r':20,
				'b':50,
				't':20,
				'pad':5
			},
			#'shapes': myShapes,
		}
		trace0 = go.Scatter(
			x = frames,
			y = diff,
			mode = 'lines+markers',
			#name = 'trial'
		)
		
		data = [trace0]
		
		fig = {
			'data': data,
			'layout': layout,
		}
		output_type = 'div'
		fileordiv = plotly.offline.plot(fig, show_link=False, filename='triggercamera_app/templates/lastplot_ard.html', output_type=output_type, auto_open=False)

		return fileordiv
	
'''
if __name__ == '__main__':
	folder = '/home/cudmore/Sites/treadmill/v1/data/'

	t = treadmillAnalysis()
	t.assignfolder(folder)
	print t.getlist()
'''