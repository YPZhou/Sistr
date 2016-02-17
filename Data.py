import ntpath
import btk
import numpy

from Screen import Screen


class Data():


	def __init__(self):	
		self.acq = None
		self.dataPath = '.'
		self.dataFile = ''
		
		
	def loadData(self, path):
		if not ntpath.isfile(path):
			print 'Can not open ' + path
			return
		
		self.dataPath, self.dataFile = ntpath.split(path)
		
		print self.dataPath
		print self.dataFile
		
		reader = btk.btkAcquisitionFileReader()
		reader.SetFilename(path)
		reader.Update()
		self.acq = reader.GetOutput()
		
		self.frequency = self.acq.GetPointFrequency()
		self.totalFrame = self.acq.GetPointFrameNumber()
		self.totalPoint = self.acq.GetPointNumber()
		
		print self.acq.GetPointFrequency()
		print self.acq.GetPointFrameNumber()
		print self.acq.GetPointNumber()