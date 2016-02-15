import os
import btk
import numpy

from Screen import Screen


class Data():


	def __init__(self):	
		self.acq = None
		self.dataPath = '.'
		self.dataFile = ''
		
		
	def loadData(self, dataPath, dataFile):
		self.dataPath = dataPath
		self.dataFile = dataFile
		
		reader = btk.btkAcquisitionFileReader()
		reader.SetFilename(os.path.join(self.dataPath, self.dataFile))
		reader.Update()
		self.acq = reader.GetOutput()
		
		print self.acq.GetPointFrequency()
		print self.acq.GetPointFrameNumber()