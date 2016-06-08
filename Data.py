import ntpath
import btk
import numpy
import sys
import copy

from PyQt4 import QtCore

from Screen import Screen


class Data(QtCore.QObject):

	
	dataLoaded = QtCore.pyqtSignal()
	dataPauseToggled = QtCore.pyqtSignal()
	dataFrameUpdated = QtCore.pyqtSignal()
	

	def __init__(self):
		super(QtCore.QObject, self).__init__()
		
		self.acq = None
		self.dataPath = '.'
		self.dataFile = ''
		
		self.paused = False
		self.currentFrame = 0
		self.maxDataValue = 0
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateTimer)
		
		
	def loadData(self, path):
		if not ntpath.isfile(path):
			print 'Can not open ' + path
			self.acq = None
			self.timer.stop()
			return
		
		self.dataPath, self.dataFile = ntpath.split(ntpath.abspath(path))
		
		try:
			reader = btk.btkAcquisitionFileReader()
			reader.SetFilename(path)
			reader.Update()
			self.acq = reader.GetOutput()
		except RuntimeError:
			print 'File format is not valid ' + path
			self.acq = None
			self.timer.stop()
			return
		
		if self.acq:
			print 'C3D file loaded ' + path
			self.frequency = self.acq.GetPointFrequency()
			self.totalFrame = self.acq.GetPointFrameNumber()
			self.totalPoint = self.acq.GetPointNumber()
		
			print 'Sample Frequency :', self.acq.GetPointFrequency()
			print 'Total Frame :', self.acq.GetPointFrameNumber()
			print 'Marker Number :', self.acq.GetPointNumber()
			
			self.maxDataValue = 0
			for i in range(self.totalPoint):
				point = self.acq.GetPoint(i)
				for j in range(self.totalFrame):
					pos = point.GetValues()[j,:]
					if pos[0] > self.maxDataValue:
						self.maxDataValue = pos[0]
					if pos[1] > self.maxDataValue:
						self.maxDataValue = pos[1]
					if pos[2] > self.maxDataValue:
						self.maxDataValue = pos[2]
			
			self.paused = False
			self.currentFrame = 0
			
			self.timer.setInterval(int(1000 / self.frequency))
			self.timer.start()
			
			self.dataLoaded.emit()
			
	
	def togglePaused(self):
		if self.acq:
			self.paused = not self.paused
			self.dataPauseToggled.emit()
	
	
	def offsetCurrentFrame(self, offset):
		if self.acq:
			self.currentFrame += offset
			if self.currentFrame >= self.totalFrame:
				self.currentFrame = 0
			elif self.currentFrame < 0:
				self.currentFrame = self.totalFrame - 1 
	
	
	def setCurrentFrame(self, currentFrame):
		if self.acq:
			self.currentFrame = currentFrame
			if self.currentFrame >= self.totalFrame:
				self.currentFrame = 0
			elif self.currentFrame < 0:
				self.currentFrame = self.totalFrame - 1 
	
	
	def speedComboBoxActivated(self, index):
		if not self.acq:
			return
		interval = 1
		if index == 0:
			interval = int(8000 / self.frequency)
		elif index == 1:
			interval = int(4000 / self.frequency)
		elif index == 2:
			interval = int(2000 / self.frequency)
		elif index == 3:
			interval = int(1000 / self.frequency)
		elif index == 4:
			interval = int(500 / self.frequency)
		elif index == 5:
			interval = int(250 / self.frequency)
		elif index == 6:
			interval = int(125 / self.frequency)
		elif index == 7:
			interval = int(62.5 / self.frequency)
		elif index == 8:
			interval = int(31.25 / self.frequency)
		elif index == 9:
			interval = int(15.625 / self.frequency)
		if interval < 1:
			interval = 1
		self.timer.setInterval(interval)
	
		
	def getCurrentFrame(self):
		return self.currentFrame	
		
		
	def getCurrentFrameData(self):
		if self.acq:				
			return self.acq.GetPoints()
		return None		
		
		
	def getMaxDataValue(self):
		return self.maxDataValue
		
		
	def createGroupFromSelection(self, selection):
		if len(selection) < 2:
			return []
		group = []
		openList = copy.copy(selection)
		closeList = [openList.pop(0)]

		while len(openList) > 0:
			minOpenIndex = -1
			minCloseIndex = -1
			minPopIndex = -1
			minDistance = sys.float_info.max
			for closept in closeList:
				pt1 = self.acq.GetPoint(closept)
				x1 = pt1.GetValues()[self.currentFrame,0]
				y1 = pt1.GetValues()[self.currentFrame,1]
				z1 = pt1.GetValues()[self.currentFrame,2]
				for i in range(len(openList)):
					openpt = openList[i]
					pt2 = self.acq.GetPoint(openpt)
					x2 = pt2.GetValues()[self.currentFrame,0]
					y2 = pt2.GetValues()[self.currentFrame,1]
					z2 = pt2.GetValues()[self.currentFrame,2]
					distance = numpy.linalg.norm([x1 - x2, y1 - y2, z1 - z2])
					if distance < minDistance:
						minOpenIndex = openpt
						minCloseIndex = closept
						minPopIndex = i
						minDistance = distance
			closeList.append(openList.pop(minPopIndex))
			group.append([minOpenIndex, minCloseIndex])
		
		return group
	
			
	def updateTimer(self):
		if self.acq and not self.paused:
			self.currentFrame += 1
			if self.currentFrame >= self.totalFrame:
				self.currentFrame = 0
			self.dataFrameUpdated.emit()