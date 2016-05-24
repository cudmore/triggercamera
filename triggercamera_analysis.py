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
		self.folder = ''
		self.list = ''
		self.dbfile = ''

	def plotfile(self,filePath):

		#date,time,seconds,event,frameNumber
		df = pd.read_csv(filePath)
		diff = np.diff(df['seconds'].astype('float'))
		diff *= 1000 #seconds to ms
		frames = df['frameNumber']

		layout = {
			'title': '',
			'xaxis': {
				#'range': [0, totalDur],
				'autotick':True,
			},
			'yaxis': {
				#'range': [0, 5],
				#'showgrid': False,
				#'ticks': '',
				#'showticklabels': False
			},
			'width': 600,
			'height': 400,
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
		fileordiv = plotly.offline.plot(fig, show_link=False, filename='triggercamera_app/templates/lastplot.html', output_type=output_type, auto_open=False)

		return fileordiv

'''
if __name__ == '__main__':
	folder = '/home/cudmore/Sites/treadmill/v1/data/'

	t = treadmillAnalysis()
	t.assignfolder(folder)
	print t.getlist()
'''