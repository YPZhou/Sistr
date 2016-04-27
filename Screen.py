from PyQt4 import QtCore, QtGui

from GLRenderArea import GLRenderArea
from Parameter import Parameter
from TimerBar import TimerBar


class ScreenManager():


	def __init__(self, data):
		self.screenList = []
		self.screenList.append(Screen(data, True))


class Screen(QtGui.QMainWindow):


	def __init__(self, data, mainWindow = False):
		super(Screen, self).__init__()
		
		self.data = data
		self.mainWindow = mainWindow
		
		if self.mainWindow:
			pass
			# print 'mainWindow'
			# self.data.loadData('.', 'Repro_geste_standard_assis_Trial1.c3d')
			# self.screenList = []
		else:
			pass
			# print 'new sub window'
		
		self.initUI()
		
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(10)
		self.timer.timeout.connect(self.updateTimer)
		self.timer.start()

		
	def initUI(self):		
		if self.mainWindow:
			self.setAcceptDrops(True)
		
			openAction = QtGui.QAction('Open', self)
			openAction.triggered.connect(self.showFileDialog)
			exitAction = QtGui.QAction('Exit', self)
			exitAction.triggered.connect(QtGui.qApp.quit)
		
			filemenu = self.menuBar().addMenu('File')
			filemenu.addAction(openAction)
			filemenu.addSeparator()
			filemenu.addAction(exitAction)
			
			self.parameterDialog = Parameter(self)
			parameterAction = QtGui.QAction('Parameter', self)
			parameterAction.triggered.connect(self.showParameterDialog)
			
			viewmenu = self.menuBar().addMenu('View')
			viewmenu.addAction(parameterAction)

		self.glRenderArea = GLRenderArea(self)
		self.centralTab = QtGui.QTabWidget()
		self.centralTab.addTab(self.glRenderArea, '3D View')
		self.centralTab.addTab(QtGui.QWidget(), '2D View')
		
		self.timerBar = TimerBar(self)
		
		self.centralLayout = QtGui.QVBoxLayout()
		self.centralLayout.addWidget(self.centralTab)
		self.centralLayout.addWidget(self.timerBar)
		
		self.centralWidget = QtGui.QWidget()
		self.centralWidget.setLayout(self.centralLayout)
		
		self.setCentralWidget(self.centralWidget)
		self.show()
		
		
	def showFileDialog(self):
		fileDialog = QtGui.QFileDialog(parent = self, caption = 'Open video file')
		if fileDialog.exec_() == QtGui.QDialog.Accepted:
			self.data.loadData(str(fileDialog.selectedFiles()[0]))
			
			
	def showParameterDialog(self):
		self.parameterDialog.show()
			
			
	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

			
	def dropEvent(self, event):
		if len(event.mimeData().urls()) > 0:
			url = event.mimeData().urls()[0]
			path = url.toLocalFile().toLocal8Bit().data()
			self.data.loadData(path)
		else:
			event.ignore()
			
			
	def updateTimer(self):
		if self.data.acq:
			self.timerBar.setPauseButtonChecked(self.data.paused)
			self.timerBar.setMaximum(self.data.totalFrame)
			self.timerBar.setValue(self.data.currentFrame)