from PyQt4 import QtCore, QtGui


class ScreenManager():


	def __init__(self, data):
		self.screenList = []
		self.screenList.append(Screen(data, True))
		# self.screenList.append(Screen(data))


class Screen(QtGui.QMainWindow):


	def __init__(self, data, mainWindow = False):
		super(Screen, self).__init__()
		
		self.data = data
		self.mainWindow = mainWindow
		
		if self.mainWindow:
			print 'mainWindow'
			# self.data.loadData('.', 'Repro_geste_standard_assis_Trial1.c3d')
			# self.screenList = []
		else:
			print 'new sub window'
		
		self.initUI()

		
	def initUI(self):
		print 'initialize UI'
		
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
		
		self.centralTab = QtGui.QTabWidget()
		# self.centralTab.setTabPosition(QtGui.QTabWidget.West)
		# self.centralTab.setTabShape(QtGui.QTabWidget.Triangular)
		self.centralTab.addTab(QtGui.QWidget(), '3D View')
		self.centralTab.addTab(QtGui.QWidget(), '2D View')
		
		self.setCentralWidget(self.centralTab)
		self.show()
		
		
	def showFileDialog(self):
		fileDialog = QtGui.QFileDialog(parent = self, caption = 'Open video file')
		if fileDialog.exec_() == QtGui.QDialog.Accepted:
			self.data.loadData(str(fileDialog.selectedFiles()[0]))
			
			
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