from PyQt4 import QtCore, QtGui


class GridCheckBox(QtGui.QCheckBox):


	def __init__(self, screen):
		pass


class ColorButton(QtGui.QPushButton):


	def __init__(self, screen):
		pass


class ItemList(QtGui.QTreeWidget):


	itemListPick = QtCore.pyqtSignal()


	def __init__(self, screen):
		super(ItemList, self).__init__(parent = screen)
		self.screen = screen
		self.itemClicked.connect(self.itemClickedHandler)
		# self.itemPressed.connect(self.itemPressedHandler)
		self.initUI()
		
		
	def initUI(self):
		self.setColumnCount(6)
		labels = ['Name', 'Draw', 'Graph', 'Traj', 'Tag', 'Color']
		self.setHeaderLabels(labels)
		self.setFixedWidth(300)
		for i in range(1, 6):
			self.setColumnWidth(i, 50)
		self.setUniformRowHeights(True)
		self.setAlternatingRowColors(True)
		self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		
		self.rootMarker = QtGui.QTreeWidgetItem(self)
		self.rootMarker.setText(0, 'Markers')
		
		
	def getRootMarkerIndex(self):
		return self.indexFromItem(self.rootMarker)
		
		
	def setItemData(self, data):
		if self.rootMarker.childCount() > 0:
			self.clear()
			self.rootMarker = QtGui.QTreeWidgetItem(self)
			self.rootMarker.setText(0, 'Markers')
		
		frameData = data.getCurrentFrameData()		
		for i in range(frameData.GetItemNumber()):
			pt = frameData.GetItem(i)
			name = pt.GetLabel()
			item = QtGui.QTreeWidgetItem(self.rootMarker)
			item.setText(0, name)
			
		self.clearSelection()
		self.itemListPick.emit()
			
			
	def itemClickedHandler(self, item, column):
		if item == self.rootMarker:
			# self.setItemSelected(item, False)
			self.clearSelection()
		self.itemListPick.emit()
		
		
	def mousePressEvent(self, event):
		item = self.itemAt(event.pos())
		if not item:
			self.clearSelection()
			self.itemListPick.emit()
		QtGui.QTreeWidget.mousePressEvent(self, event)