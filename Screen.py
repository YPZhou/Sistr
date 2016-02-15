from PyQt4 import QtCore, QtGui


class ScreenManager():


	def __init__(self, data):
		self.screenList = []
		self.screenList.append(Screen(), data, True)
		self.screenList.append(Screen(), data)


class Screen(QtGui.QMainWindow):


	def __init__(self, data, mainWindow = False):
		super(Screen, self).__init__()
		
		self.data = data
		self.mainWindow = mainWindow
		
		if self.mainWindow:
			print 'mainWindow'
			self.data.loadData('.', 'Repro_geste_standard_assis_Trial1.c3d')
			# self.screenList = []
		else:
			print 'new sub window'
		
		self.initUI()

		
	def initUI(self):
		print 'initialize UI'
		
		# if self.mainWindow:
			# self.screenList.append(Screen(self.data))
		
		self.centralTab = QtGui.QTabWidget()
		# self.centralTab.setTabPosition(QtGui.QTabWidget.West)
		# self.centralTab.setTabShape(QtGui.QTabWidget.Triangular)
		self.centralTab.addTab(QtGui.QWidget(), '3D View')
		self.centralTab.addTab(QtGui.QWidget(), '2D View')		
		
		self.setCentralWidget(self.centralTab)
		self.show()