import plotly
print 'plotly.__version__=', plotly.__version__  # version >1.9.4 required
import plotly.graph_objs as go

import pandas
import numpy as np
import os.path

def myplotlyplot(filePath,output_type):
	'''output_type: {filePath, div}'''
	
	print 'myplotlyplot()', filePath
	
	#read data, row 1 is column headers
	print '\tpandas.read_csv'
	df = pandas.read_csv(filePath, header=1)

	print '\tparsing'
	#get millis of rows labeled scanimageframe
	xTrial = df[(df['event'] == 'startTrial') | (df['event']=='stopTrial')].millis
	xFrames = df[df['event']=='scanimageframe'].millis
	xMotor = df[(df['event'] == 'motorstart') | (df['event']=='motorstop')].millis
	xRotary = df[(df['event'] == 'rotary')].millis

	#normalize to startTrial and convert to seconds
	startMillis = xTrial.iloc[0]
	xTrial -= startMillis 
	xFrames -= startMillis 
	xMotor -= startMillis 
	xRotary -= startMillis 
	
	xTrial /= 1000 
	xFrames /= 1000 
	xMotor /= 1000 
	xRotary /= 1000 

	# number of rows
	numTrial = xTrial.count()
	numFrames = xFrames.count()
	numMotor = xMotor.count()
	numRotary = xRotary.count()
	
	#fake out some y values
	yTrial = np.zeros(numTrial) + 1
	yFrames = np.zeros(numFrames) + 2
	yMotor = np.zeros(numMotor) + 3
	yRotary = np.zeros(numRotary) + 4
		
	#vertical line for each scanimage frame
	xFrames2 = np.empty(numFrames*3)
	yFrames2 = np.empty(numFrames*3)
	outIdx = 0
	for i in xFrames:
		xFrames2[outIdx] = i
		xFrames2[outIdx+1] = i
		xFrames2[outIdx+2] = None
		yFrames2[outIdx] = 0
		yFrames2[outIdx+1] = 5
		yFrames2[outIdx+2] = None
		outIdx += 3
		
	'''
	layout = go.Layout(
			title = "file:" + filePath,
			yaxis = dict(range=[0.5,4.5])
		)
	'''

	layout = {
	
		'title': 'file:' + filePath,
		'xaxis': {
			#'range': [0, 9],
			'zeroline': False,
		},
		'yaxis': {
			'range': [0, 5],
			'showgrid': False,
		},
		'width': 500,
		'height': 300,
	}

	layout['shapes'] = []
	for i in np.arange(0, numMotor-1, 2):
		myrect = {
			'type': 'rect',
			# x-reference is assigned to the x-values
			'xref': 'x',
			# y-reference is assigned to the plot paper [0,1]
			'yref': 'paper',
			'x0': xMotor.iloc[i],
			'y0': 0,
			'x1': xMotor.iloc[i+1],
			'y1': 1,
			'fillcolor': '#888888',
			'opacity': 0.6,
			'line': {
				'width': 0,
			}
		}
		#print xMotor.iloc[i]
		layout['shapes'].append(myrect)
		i += 1
		
	#layout['shapes'] = [myrect,]

	trace0 = go.Scatter(
		x = xTrial,
		y = yTrial,
		mode = 'lines+markers',
		name = 'trial'
	)
	trace1 = go.Scatter(
		x = xFrames2,
		y = yFrames2,
		mode = 'lines',
		name = 'frames',
		marker = dict(
			size = 10,
			color = 'rgba(50, 255, 50, .9)',
			line = dict(
				width = 2,
			)
		)
	)
	trace2 = go.Scatter(
		x = xMotor,
		y = yMotor,
		mode = 'lines+markers',
		name = 'motor'
	)
	trace3 = go.Scatter(
		x = xRotary,
		y = yRotary,
		mode = 'markers',
		name = 'rotary'
	)
	
	data = [trace0, trace1, trace2, trace3]

	#fig = go.Figure(data=data, layout=layout)
	fig = {
		'data': data,
		'layout': layout,
	}
	
	#output_type = 'file'
	#output_type = 'div'
	
	fileordiv = plotly.offline.plot(fig, filename='templates/xxx.html', output_type=output_type, auto_open=False)

	return fileordiv
	
if __name__ == '__main__':
	file = 'data/20160306_211227_t4_d.txt'
	myplotlyplot(file)
