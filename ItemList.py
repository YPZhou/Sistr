from PyQt4 import QtCore, QtGui


class ListCheckBox(QtGui.QCheckBox):


	listChkBoxStateChanged = QtCore.pyqtSignal(object)


	def __init__(self, modelIndex, chkBoxType):
		super(ListCheckBox, self).__init__()
		self.modelIndex = modelIndex
		self.chkBoxType = chkBoxType
		self.stateChanged.connect(self.chkBoxStateChanged)
		
		
	def chkBoxStateChanged(self, state):
		self.listChkBoxStateChanged.emit([self.modelIndex, self.chkBoxType, state])


class ColorButton(QtGui.QPushButton):


	colorChanged = QtCore.pyqtSignal(object)


	def __init__(self, modelIndex, color = None):
		super(ColorButton, self).__init__()
		self.modelIndex = modelIndex
		self.color = color
		if self.color:
			self.setColor(self.color)
		self.pressed.connect(self.colorDialog)
		
		
	def setColor(self, color):
		if color != self.color:
			self.color = color
			self.colorChanged.emit([self.modelIndex, 'color', self.color])
			
		if self.color:
			self.setStyleSheet('background-color: %s;' % self.color.name())
		else:
			self.setStyleSheet('')
			
			
	def colorDialog(self):
		dlg = QtGui.QColorDialog()
		if self.color:
			dlg.setCurrentColor(QtGui.QColor(self.color))
		if dlg.exec_():
			self.setColor(dlg.currentColor())


class ItemList(QtGui.QTreeWidget):


	itemListPick = QtCore.pyqtSignal()
	itemConfigChanged = QtCore.pyqtSignal(object)


	def __init__(self, screen):
		super(ItemList, self).__init__(parent = screen)
		self.screen = screen
		self.itemClicked.connect(self.itemClickedHandler)
		
		self.setFocusPolicy(QtCore.Qt.NoFocus)
		
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
		
		self.rootGroup = QtGui.QTreeWidgetItem(self)
		self.rootGroup.setText(0, 'Groups')
		
		
	def getRootMarkerIndex(self):
		return self.indexFromItem(self.rootMarker)
		
		
	def clearPick(self):
		self.clearSelection()
		for i in range(self.rootMarker.childCount()):
			self.rootMarker.child(i).setTextColor(0, QtGui.QColor(0, 0, 0, 255))
		
		
	def setItemData(self, data):
		if self.rootMarker.childCount() > 0:
			self.clear()
			self.rootMarker = QtGui.QTreeWidgetItem(self)
			self.rootMarker.setText(0, 'Markers')
			self.rootGroup = QtGui.QTreeWidgetItem(self)
			self.rootGroup.setText(0, 'Groups')
		
		frameData = data.getCurrentFrameData()		
		for i in range(frameData.GetItemNumber()):
			pt = frameData.GetItem(i)
			name = pt.GetLabel()
			item = QtGui.QTreeWidgetItem(self.rootMarker)
			item.setText(0, name)
			index = self.indexFromItem(item)
			maskDrawChkBox = ListCheckBox(index, 'draw')
			maskDrawChkBox.setCheckState(QtCore.Qt.Checked)
			maskGraphChkBox = ListCheckBox(index, 'graph')
			maskTrajChkBox = ListCheckBox(index, 'traj')
			maskTagChkBox = ListCheckBox(index, 'tag')
			colorBtn = ColorButton(index)
			maskDrawChkBox.listChkBoxStateChanged.connect(self.itemListStateChanged)
			maskGraphChkBox.listChkBoxStateChanged.connect(self.itemListStateChanged)
			maskTrajChkBox.listChkBoxStateChanged.connect(self.itemListStateChanged)
			maskTagChkBox.listChkBoxStateChanged.connect(self.itemListStateChanged)
			colorBtn.colorChanged.connect(self.itemListStateChanged)
			self.setItemWidget(item, 1, maskDrawChkBox)
			self.setItemWidget(item, 2, maskGraphChkBox)
			self.setItemWidget(item, 3, maskTrajChkBox)
			self.setItemWidget(item, 4, maskTagChkBox)
			self.setItemWidget(item, 5, colorBtn)
			
			
		self.clearPick()
		self.itemListPick.emit()
			
			
	def itemClickedHandler(self, item, column):
		if item == self.rootMarker or item == self.rootGroup:
			self.clearPick()
		if self.isItemSelected(item):
			item.setTextColor(0, QtGui.QColor(0, 180, 50, 150))
		else:
			item.setTextColor(0, QtGui.QColor(0, 0, 0, 255))
		self.itemListPick.emit()
		
		
	def mousePressEvent(self, event):
		item = self.itemAt(event.pos())
		if not item:
			self.clearPick()			
			self.itemListPick.emit()
		QtGui.QTreeWidget.mousePressEvent(self, event)
		
		
	def itemListStateChanged(self, item):
		self.itemConfigChanged.emit(item)