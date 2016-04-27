from PyQt4 import QtCore, QtGui


class JumpSlider(QtGui.QSlider):
	def __init__(self, orientation):
		super(JumpSlider, self).__init__(orientation)
		self.setMinimumHeight(70);
		
		
	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			opt = QtGui.QStyleOptionSlider()
			self.initStyleOption(opt)
			sr = self.style().subControlRect(QtGui.QStyle.CC_Slider, opt, QtGui.QStyle.SC_SliderHandle, self)
			halfHandleWidth = (0.5 * sr.width()) + 0.5
			adaptedPosX = event.x()
			if adaptedPosX < halfHandleWidth:
				adaptedPosX = halfHandleWidth
			if adaptedPosX > self.width() - halfHandleWidth:
				adaptedPosX = self.width() - halfHandleWidth
					
			newWidth = (self.width() - halfHandleWidth) - halfHandleWidth
			normalizedPosition = (adaptedPosX - halfHandleWidth)  / newWidth

			newVal = self.minimum() + ((self.maximum() - self.minimum()) * normalizedPosition)
			self.setValue(newVal)

			event.accept()
		QtGui.QSlider.mousePressEvent(self, event)
		
		
class TimerBar(QtGui.QWidget):
	def __init__(self, screen):
		super(TimerBar, self).__init__()
		self.screen = screen
		self.initUI()
		
		
	def initUI(self):
		self.timeSlider = JumpSlider(QtCore.Qt.Horizontal)
		self.timeSlider.setMinimum(1)
		self.timeSlider.setMaximum(1)
		# self.timeSlider.setMaximum(self.syncTimer.viconData.frameCount - 1)
		self.timeSlider.valueChanged[int].connect(self.screen.data.setCurrentFrame)
		
		self.frameLabel = QtGui.QLabel()
		self.frameLabel.setFixedWidth(50)
		self.frameLabel.setAlignment(QtCore.Qt.AlignCenter)
		
		self.videoFrameLabel = QtGui.QLabel()
		self.videoFrameLabel.setFixedWidth(50)
		self.videoFrameLabel.setAlignment(QtCore.Qt.AlignCenter)
		
		self.pauseButton = QtGui.QPushButton('Pause')
		self.pauseButton.setCheckable(True)
		self.pauseButton.clicked.connect(self.screen.data.togglePaused)
		
		self.spdComboBox = QtGui.QComboBox()
		self.spdComboBox.addItem('1/8')
		self.spdComboBox.addItem('1/4')
		self.spdComboBox.addItem('1/2')
		self.spdComboBox.addItem('1')
		self.spdComboBox.addItem('2')
		self.spdComboBox.addItem('4')
		self.spdComboBox.addItem('8')
		self.spdComboBox.addItem('16')
		self.spdComboBox.addItem('32')
		self.spdComboBox.addItem('64')
		self.spdComboBox.setCurrentIndex(3)
		self.spdComboBox.activated.connect(self.screen.data.speedComboBoxActivated)
		
		self.vboxLeft = QtGui.QVBoxLayout()
		self.vboxLeft.addWidget(self.pauseButton)
		self.vboxLeft.addWidget(self.spdComboBox)
		self.vboxLeft.setContentsMargins(0, 0, 0, 0)
		
		self.constrainWidget = QtGui.QWidget()
		self.constrainWidget.setFixedWidth(60)
		self.constrainWidget.setLayout(self.vboxLeft)
		self.constrainWidget.setContentsMargins(0, 0, 0, 0)
		
		self.vboxLabel = QtGui.QVBoxLayout()
		self.vboxLabel.addWidget(self.frameLabel)
		self.vboxLabel.addWidget(self.videoFrameLabel)

		self.vboxRight = QtGui.QVBoxLayout()
		self.vboxRight.addWidget(self.timeSlider)
		self.vboxRight.setContentsMargins(0, 0, 0, 0)
		
		self.hboxMain = QtGui.QHBoxLayout()
		self.hboxMain.addWidget(self.constrainWidget)
		self.hboxMain.addLayout(self.vboxLabel)
		self.hboxMain.addLayout(self.vboxRight)
		self.hboxMain.setContentsMargins(0, 0, 0, 0)
		
		self.setLayout(self.hboxMain)
		
		
	def setMaximum(self, max):
		if self.timeSlider.maximum() == 0 or self.timeSlider.maximum() != max:
			self.timeSlider.setMaximum(max)
			self.update()
			
			
	def setValue(self, value):
		if value >= self.timeSlider.minimum() and value <= self.timeSlider.maximum():
			self.timeSlider.setValue(value)
			
			
	def setPauseButtonChecked(self, checked):
		self.pauseButton.setChecked(checked)
		if checked:
			self.pauseButton.setText('Resume')
		else:
			self.pauseButton.setText('Pause')
		
		
	def paintEvent(self, event):
		if self.screen.data.acq:
			opt = QtGui.QStyleOptionSlider()
			self.timeSlider.initStyleOption(opt)
			sr = self.style().subControlRect(QtGui.QStyle.CC_Slider, opt, QtGui.QStyle.SC_SliderHandle, self)
			halfHandleWidth = (0.5 * sr.width()) + 0.5
		
			painter = QtGui.QPainter(self)
			painter.setRenderHint(QtGui.QPainter.Antialiasing)
			
			painter.setPen(QtCore.Qt.black)
			# scaleCount = self.timeSlider.geometry().width() / 50
			scaleCount = 20
			metrics = QtGui.QFontMetrics(self.font())
			for i in range(scaleCount):
				value = int((float)(self.screen.data.totalFrame - 1) / (scaleCount - 1) * i)
				position = QtGui.QStyle.sliderPositionFromValue(self.timeSlider.minimum(), self.timeSlider.maximum(), value, self.timeSlider.width() - halfHandleWidth * 2)
				painter.drawLine(position + self.timeSlider.geometry().x() + halfHandleWidth, 15, position + self.timeSlider.geometry().x() + halfHandleWidth, 50)
				painter.drawText(position + self.timeSlider.geometry().x() + halfHandleWidth - 25, 55, 50, 10, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, str(value))