from PyQt4 import QtGui

from Config import *


class Parameter(QtGui.QDialog):


	def __init__(self, parent):
		super(Parameter, self).__init__(parent)
		self.initUI()
		
		
	def initUI(self):
		self.setWindowTitle('Display parameters')
		
		self.verticalFOVLabel = QtGui.QLabel('Vertical FOV')
		self.horizontalFOVLabel = QtGui.QLabel('Horizontal FOV')
		self.nearPlaneLabel = QtGui.QLabel('Near Plane')
		self.farPlaneLabel = QtGui.QLabel('Far Plane')
		self.pointSizeLabel = QtGui.QLabel('Point size')
		self.segmentWidthLabel = QtGui.QLabel('Segment Width')
		self.coneAngleLabel = QtGui.QLabel('Cone Radius (deg)')
		self.coneTransparencyLabel = QtGui.QLabel('Cone Transparency')
		self.gridLineCountLabel = QtGui.QLabel('Grid Line Count')
		self.gridWidthLabel = QtGui.QLabel('Grid Width')
		self.gridSpacingLabel = QtGui.QLabel('Grid Spacing (mm)')
		self.gridVisibilityLabel = QtGui.QLabel('Grid Visibility')
		self.axisWidthLabel = QtGui.QLabel('Axis Width')
		self.axisVisibilityLabel = QtGui.QLabel('Axis Visibility')
		self.trajectoryWidthLabel = QtGui.QLabel('Trajectory Width')
		self.trajectoryLengthLabel = QtGui.QLabel('Trajectory Length')
		self.scrollSpeedLabel = QtGui.QLabel('Scroll Speed')
		
		self.verticalFOVLineEdit = QtGui.QLineEdit(str(VERTICAL_FOV))
		self.horizontalFOVLineEdit = QtGui.QLineEdit(str(HORIZONTAL_FOV))
		self.nearPlaneLineEdit = QtGui.QLineEdit(str(NEAR_PLANE))
		self.farPlaneLineEdit = QtGui.QLineEdit(str(FAR_PLANE))
		self.pointSizeLineEdit = QtGui.QLineEdit(str(POINT_SIZE))
		self.segmentWidthLineEdit = QtGui.QLineEdit(str(SEGMENT_WIDTH))
		self.coneAngleLineEdit = QtGui.QLineEdit(str(CONE_ANGLE))
		self.coneTransparencyLineEdit = QtGui.QLineEdit(str(CONE_TRANSPARENCY))
		self.gridLineCountLineEdit = QtGui.QLineEdit(str(GRID_LINE_COUNT))
		self.gridWidthLineEdit = QtGui.QLineEdit(str(GRID_WIDTH))
		self.gridSpacingLineEdit = QtGui.QLineEdit(str(GRID_SPACING))
		self.gridVisibilityCheckBox = QtGui.QCheckBox()
		self.gridVisibilityCheckBox.setChecked(GRID_VISIBILITY)
		self.axisWidthLineEdit = QtGui.QLineEdit(str(AXIS_WIDTH))
		self.axisVisibilityCheckBox = QtGui.QCheckBox()
		self.axisVisibilityCheckBox.setChecked(AXIS_VISIBILITY)
		self.trajectoryWidthLineEdit = QtGui.QLineEdit(str(TRAJECTORY_WIDTH))
		self.trajectoryLengthLineEdit = QtGui.QLineEdit(str(TRAJECTORY_LENGTH))
		self.scrollSpeedLineEdit = QtGui.QLineEdit(str(SCROLL_SPEED))
		
		self.gridLayout = QtGui.QGridLayout()
		self.gridLayout.addWidget(self.verticalFOVLabel, 0, 0)
		self.gridLayout.addWidget(self.horizontalFOVLabel, 1, 0)
		self.gridLayout.addWidget(self.nearPlaneLabel, 2, 0)
		self.gridLayout.addWidget(self.farPlaneLabel, 3, 0)
		self.gridLayout.addWidget(self.pointSizeLabel, 4, 0)
		self.gridLayout.addWidget(self.segmentWidthLabel, 5, 0)
		self.gridLayout.addWidget(self.coneAngleLabel, 6, 0)
		self.gridLayout.addWidget(self.coneTransparencyLabel, 7, 0)
		self.gridLayout.addWidget(self.gridLineCountLabel, 8, 0)
		self.gridLayout.addWidget(self.gridWidthLabel, 9, 0)
		self.gridLayout.addWidget(self.gridSpacingLabel, 10, 0)
		self.gridLayout.addWidget(self.gridVisibilityLabel, 11, 0)
		self.gridLayout.addWidget(self.axisWidthLabel, 12, 0)
		self.gridLayout.addWidget(self.axisVisibilityLabel, 13, 0)
		self.gridLayout.addWidget(self.trajectoryWidthLabel, 14, 0)
		self.gridLayout.addWidget(self.trajectoryLengthLabel, 15, 0)
		self.gridLayout.addWidget(self.scrollSpeedLabel, 16, 0)
		self.gridLayout.addWidget(self.verticalFOVLineEdit, 0, 1)
		self.gridLayout.addWidget(self.horizontalFOVLineEdit, 1, 1)
		self.gridLayout.addWidget(self.nearPlaneLineEdit, 2, 1)
		self.gridLayout.addWidget(self.farPlaneLineEdit, 3, 1)
		self.gridLayout.addWidget(self.pointSizeLineEdit, 4, 1)
		self.gridLayout.addWidget(self.segmentWidthLineEdit, 5, 1)
		self.gridLayout.addWidget(self.coneAngleLineEdit, 6, 1)
		self.gridLayout.addWidget(self.coneTransparencyLineEdit, 7, 1)
		self.gridLayout.addWidget(self.gridLineCountLineEdit, 8, 1)
		self.gridLayout.addWidget(self.gridWidthLineEdit, 9, 1)
		self.gridLayout.addWidget(self.gridSpacingLineEdit, 10, 1)
		self.gridLayout.addWidget(self.gridVisibilityCheckBox, 11, 1)
		self.gridLayout.addWidget(self.axisWidthLineEdit, 12, 1)
		self.gridLayout.addWidget(self.axisVisibilityCheckBox, 13, 1)
		self.gridLayout.addWidget(self.trajectoryWidthLineEdit, 14, 1)
		self.gridLayout.addWidget(self.trajectoryLengthLineEdit, 15, 1)
		self.gridLayout.addWidget(self.scrollSpeedLineEdit, 16, 1)
		
		self.setLayout(self.gridLayout)
		
		
	def getVerticalFOV(self):
		try:
			return max(float(self.verticalFOVLineEdit.text()), 1)
		except ValueError:
			return VERTICAL_FOV
			
			
	def getHorizontalFOV(self):
		try:
			return max(float(self.horizontalFOVLineEdit.text()), 1)
		except ValueError:
			return HORIZONTAL_FOV
			
	
	def getNearPlane(self):
		try:
			return float(self.nearPlaneLineEdit.text())
		except ValueError:
			return NEAR_PLANE
			
	
	def getFarPlane(self):
		try:
			return float(self.farPlaneLineEdit.text())
		except ValueError:
			return FAR_PLANE
			
	
	def getPointSize(self):
		try:
			return float(self.pointSizeLineEdit.text())
		except ValueError:
			return POINT_SIZE
			
		
	def getSegmentWidth(self):
		try:
			return float(self.segmentWidthLineEdit.text())
		except ValueError:
			return SEGMENT_WIDTH
			
			
	def getConeAngle(self):
		try:
			return float(self.coneAngleLineEdit.text())
		except ValueError:
			return CONE_ANGLE
			
			
	def getConeTransparency(self):
		try:
			return float(self.coneTransparencyLineEdit.text())
		except ValueError:
			return CONE_TRANSPARENCY
			
		
	def getGridLineCount(self):
		try:
			return float(self.gridLineCountLineEdit.text())
		except ValueError:
			return GRID_LINE_COUNT
			
		
	def getGridWidth(self):
		try:
			return float(self.gridWidthLineEdit.text())
		except ValueError:
			return GRID_WIDTH
			
		
	def getGridSpacing(self):
		try:
			return float(self.gridSpacingLineEdit.text())
		except ValueError:
			return GRID_SPACING
			
		
	def getGridVisibility(self):
		return self.gridVisibilityCheckBox.checkState() == 2
	
	
	def getAxisWidth(self):
		try:
			return float(self.axisWidthLineEdit.text())
		except ValueError:
			return AXIS_WIDTH
			
	
	def getAxisVisibility(self):
		return self.axisVisibilityCheckBox.checkState() == 2
	
	
	def getTrajectoryWidth(self):
		try:
			return float(self.trajectoryWidthLineEdit.text())
		except ValueError:
			return TRAJECTORY_WIDTH
			
			
	def getTrajectoryLength(self):
		try:
			return int(self.trajectoryLengthLineEdit.text())
		except ValueError:
			return TRAJECTORY_LENGTH
			
	
	def getScrollSpeed(self):
		try:
			return float(self.scrollSpeedLineEdit.text())
		except ValueError:
			return SCROLL_SPEED