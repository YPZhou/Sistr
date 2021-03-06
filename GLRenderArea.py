import math, numpy

from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL import GL, GLU
from OpenGL.GL import shaders

from Camera import Camera


# In order to be compatible with OS X, all shaders are written in GLSL version 120.
# On OS X, only 2 versions of OpenGL is supported : the legacy 2.1 and the core version,
# which is totally dependant of the graphic card. Any OpenGL version in between is not supported.
VERTEX_SHADER = """
#version 120

attribute vec3 pos;
attribute vec4 vertex_color;
varying vec4 frag_color;
uniform mat4 mvp;

void main()
{
	vec4 v = vec4(pos, 1);
	frag_color = vertex_color;
	gl_Position = mvp * v;
}
"""

FRAGMENT_SHADER = """
#version 120

varying vec4 frag_color;

void main()
{
	gl_FragColor = frag_color;
}
"""

FRAGMENT_MARKER_SHADER = """
#version 120

varying vec4 frag_color;

void main()
{
	/*vec2 coord = gl_PointCoord - vec2(0.5);
	if (length(coord) > 0.5)
		discard;*/
	gl_FragColor = frag_color;
	/*gl_FragColor.a = 0.5 - length(coord);*/
}
"""


class GLRenderArea(QtOpenGL.QGLWidget):

	def __init__(self, screen):
		# Explicitly ask for legacy OpenGL version to keep maximum compatibility across different operating systems
		fmt = QtOpenGL.QGLFormat()
		fmt.setVersion(2, 1)
		fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
		fmt.setSampleBuffers(True)		
		super(GLRenderArea, self).__init__(fmt, parent = screen)
	
		self.setAutoFillBackground(False)
		self.setFocusPolicy(QtCore.Qt.ClickFocus)
	
		self.xRot = 0.0
		self.yRot = 0.0
		self.zRot = 0.0
		
		self.xTrans = 0.0
		self.yTrans = 0.0
		self.zTrans = 0.0
		
		self.lastPos = QtCore.QPoint()
		self.mouseMoved = False
		self.mousePickRectStart = False
		self.ctrlPressed = False
		self.shiftPressed = False
		self.mouseRect = []
		
		self.autoCam = False
		self.ortho = False
		self.camName = ''
		self.cameraPos = (0, 0, -1)
		self.targetPos = (0, 0, 0)
		
		self.testVertexBuffer = []
		self.testColorBuffer = []
		
		# self.vw = 0
		# self.vh = 0
		
		self.camera = Camera()
		self.screen = screen
				
		self.programCompiled = False
		
		self.currentFrame = 0
		self.frameData = None
		
		self.groups = []
		
		self.selectedMarkers = set([])
		self.selectedGroups = set([])
		self.maskDraw = set([])
		self.maskTraj = set([])
		self.maskTag = set([])
		self.colorDict = {}
		
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(10)
		self.timer.timeout.connect(self.updateTimer)
		self.timer.start()


	def closeEvent(self, event):
		print 'glArea closing'
		self.timer.stop()
		print 'glArea closed'
		
		
	def minimumSizeHint(self):
		return QtCore.QSize(800, 600)
		
		
	def addGroup(self, newGroup):
		if len(newGroup) > 0:
			self.groups.append(newGroup)
		

	def paintEvent(self, event):	
		# On OS X, when using QGLWidget, it is possible that the opengl draw framebuffer is not
		# completely constructed before entering paint event.
		# We just omit all paint event before framebuffer is fully initialized.
		if GL.glCheckFramebufferStatus(GL.GL_DRAW_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
			return
			
		# Need this to make sure we are drawing on the correct GL context	
		self.makeCurrent()
		
		# Compile and link shaders only when OpenGL draw framebuffer is constructed
		if not self.programCompiled:
			self.vertexShader = shaders.compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER)
			self.fragmentShader = shaders.compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER)
			self.fragmentMarkerShader = shaders.compileShader(	FRAGMENT_MARKER_SHADER, GL.GL_FRAGMENT_SHADER)
			self.shader = shaders.compileProgram(self.vertexShader, self.fragmentShader)
			self.markerShader = shaders.compileProgram(self.vertexShader, self.fragmentMarkerShader)
			self.programCompiled = True
	
		GL.glShadeModel(GL.GL_FLAT)
		GL.glEnable(GL.GL_DEPTH_TEST)

		GL.glEnable(GL.GL_POINT_SMOOTH)
		GL.glHint(GL.GL_POINT_SMOOTH_HINT, GL.GL_NICEST)
		GL.glEnable(GL.GL_LINE_SMOOTH)
		GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		
		tv = math.tan(self.screen.parameterDialog.getVerticalFOV() * 0.5 / 180 * math.pi)
		th = math.tan(self.screen.parameterDialog.getHorizontalFOV() * 0.5 / 180 * math.pi)
		viewport_width = self.width()
		viewport_height = int(viewport_width * (tv / th))
		GL.glViewport((self.width() - viewport_width) / 2, (self.height() - viewport_height) / 2, viewport_width, viewport_height)
		
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		
		self.updateCamera()				
		self.drawCoords()
		# self.drawCones()
		self.drawMarkers()
		self.drawGroups()
		
		GL.glDisable(GL.GL_CULL_FACE)
		GL.glDisable(GL.GL_DEPTH_TEST)
		
		GL.glPointSize(5)
		self.openGLDraw(self.shader, GL.GL_LINES, self.testVertexBuffer, self.testColorBuffer)
		
		painter = QtGui.QPainter(self)
		if len(self.mouseRect) > 0:
			painter.setPen(QtGui.QColor(0, 200, 50, 100))
			left = min(self.mouseRect[0].x(), self.mouseRect[1].x())
			top = min(self.mouseRect[0].y(), self.mouseRect[1].y())
			width = max(self.mouseRect[0].x(), self.mouseRect[1].x()) - left
			height = max(self.mouseRect[0].y(), self.mouseRect[1].y()) - top
			rect = QtCore.QRect(left, top, width, height)
			painter.drawRect(rect)
		painter.end()
		
		
	def updateCamera(self):
		if self.autoCam:
			camPos = (self.syncTimer.viconData.getValue(self.currentFrame, 'Cam:' + self.camName + ':O:Y'), self.syncTimer.viconData.getValue(self.currentFrame, 'Cam:' + self.camName + ':O:Z'), self.syncTimer.viconData.getValue(self.currentFrame, 'Cam:' + self.camName + ':O:X'))
			camTarget = (self.syncTimer.viconData.getValue(self.currentFrame, 'Cam:' + self.camName + ':X:Y'), self.syncTimer.viconData.getValue(self.currentFrame, 'Cam:' + self.camName + ':X:Z'), self.syncTimer.viconData.getValue(self.currentFrame, 'Cam:' + self.camName + ':X:X'))
			self.camera.setCamPos((camPos[0] / self.syncTimer.viconData.max3D, camPos[1] / self.syncTimer.viconData.max3D, camPos[2] / self.syncTimer.viconData.max3D))
			self.camera.setTargetPos((camTarget[0] / self.syncTimer.viconData.max3D, camTarget[1] / self.syncTimer.viconData.max3D, camTarget[2] / self.syncTimer.viconData.max3D))
			
			self.camera.setRotY(0)
			self.camera.setRotZ(0)
			self.camera.setTransX(0)
			self.camera.setTransY(0)
			self.camera.setTransZ(0)

			self.xRot = 0.0
			self.yRot = 0.0
			self.zRot = 0.0
			
			self.xTrans = 0.0
			self.yTrans = 0.0
			self.zTrans = 0.0
			
			self.camera.setOrtho(False)
		else:
			self.camera.setCamPos((0, -1, 0))
			self.camera.setTargetPos((0, 0, 0))
			self.camera.setRotY(self.yRot / 16)
			self.camera.setRotZ(self.zRot / 16)
			self.camera.setTransX(self.xTrans * 0.01)
			self.camera.setTransY(self.yTrans * 0.01)
			self.camera.setTransZ(self.zTrans * 0.01)
			self.camera.setOrtho(self.ortho)
			
		self.camera.setFovH(self.screen.parameterDialog.getHorizontalFOV())
		self.camera.setFovV(self.screen.parameterDialog.getVerticalFOV())
		
		
	def drawCoords(self):
		GL.glDisable(GL.GL_DEPTH_TEST)
		spacing = 1
		max = 5
		if self.screen.data.acq:
			spacing = self.screen.parameterDialog.getGridSpacing() / self.screen.data.maxDataValue
			max = spacing * self.screen.parameterDialog.getGridLineCount()
		
		if self.screen.parameterDialog.getGridVisibility() and self.screen.parameterDialog.getGridWidth() > 0 and self.screen.parameterDialog.getGridLineCount() > 0:				
			vertexBuffer = []
			vertexBuffer.append((-max, 0, 0))
			vertexBuffer.append((max, 0, 0))
			vertexBuffer.append((0, -max, 0))
			vertexBuffer.append((0, max, 0))
			for i in numpy.arange(spacing, max + spacing * 0.5, spacing):
				vertexBuffer.append((-max, i, 0))
				vertexBuffer.append((max, i, 0))
				vertexBuffer.append((-max, -i, 0))
				vertexBuffer.append((max, -i, 0))
			
				vertexBuffer.append((i, -max, 0))
				vertexBuffer.append((i, max, 0))
				vertexBuffer.append((-i, -max, 0))
				vertexBuffer.append((-i, max, 0))
				
			colorBuffer = numpy.empty(len(vertexBuffer) * 4)
			colorBuffer.fill(0.6)
			
			GL.glLineWidth (self.screen.parameterDialog.getGridWidth())
			self.openGLDraw(self.shader, GL.GL_LINES, vertexBuffer, colorBuffer)	
		
		if self.screen.parameterDialog.getAxisVisibility():
			vertexBuffer = []
			vertexBuffer.append((0, 0, 0))
			vertexBuffer.append((max, 0, 0))
			vertexBuffer.append((0, 0, 0))
			vertexBuffer.append((0, max, 0))
			vertexBuffer.append((0, 0, 0))
			vertexBuffer.append((0, 0, max))
			
			colorBuffer = []
			colorBuffer.append((1, 0, 0, 0.4))
			colorBuffer.append((1, 0, 0, 0.4))
			colorBuffer.append((0, 1, 0, 0.4))
			colorBuffer.append((0, 1, 0, 0.4))
			colorBuffer.append((0, 0, 1, 0.4))
			colorBuffer.append((0, 0, 1, 0.4))
			
			GL.glLineWidth (self.screen.parameterDialog.getAxisWidth())
			self.openGLDraw(self.shader, GL.GL_LINES, vertexBuffer, colorBuffer)
		
		
	def drawMarkers(self):
		if self.frameData and self.screen.parameterDialog.getPointSize() > 0:
			vertexBuffer = []
			colorBuffer = []
			trajVertexBuffer = []
			trajVertexStart = []
			trajVertexCount = []
			trajColorBuffer = []
			
			GL.glDisable(GL.GL_DEPTH_TEST)
			
			maxVal = self.screen.data.getMaxDataValue()
			for i in range(self.frameData.GetItemNumber()):
				if not i in self.maskDraw:
					pt = self.frameData.GetItem(i)
					color = (1, 1, 1, 1)
					if i in self.colorDict:
						color = (self.colorDict[i].redF(), self.colorDict[i].greenF(), self.colorDict[i].blueF(), self.colorDict[i].alphaF())
					if i in self.selectedMarkers:
						color = (1.0, 0.2, 0.8, 1)
					
					colorBuffer.append(color[0])
					colorBuffer.append(color[1])
					colorBuffer.append(color[2])
					colorBuffer.append(color[3])					
					
					x = pt.GetValue(self.currentFrame, 0) / maxVal
					y = pt.GetValue(self.currentFrame, 1) / maxVal
					z = pt.GetValue(self.currentFrame, 2) / maxVal
					vertexBuffer.append(x)
					vertexBuffer.append(y)
					vertexBuffer.append(z)
					
					if not i in self.maskTraj and self.screen.parameterDialog.getTrajectoryLength() > 0:
						lowBound = max(0, self.currentFrame - self.screen.parameterDialog.getTrajectoryLength())
						highBound = min(self.screen.data.totalFrame - 1, self.currentFrame + self.screen.parameterDialog.getTrajectoryLength())
						
						if len(trajVertexCount) != 0:
							trajVertexStart.append(trajVertexStart[-1] + trajVertexCount[-1])
						else:
							trajVertexStart.append(0)
						trajVertexCount.append(0)
						for j in range(lowBound, highBound+1):
							trajVertexBuffer.append(pt.GetValue(j, 0) / maxVal)
							trajVertexBuffer.append(pt.GetValue(j, 1) / maxVal)
							trajVertexBuffer.append(pt.GetValue(j, 2) / maxVal)
							trajColorBuffer.append(color[0])
							trajColorBuffer.append(color[1])
							trajColorBuffer.append(color[2])
							trajColorBuffer.append(color[3])
							trajVertexCount[-1] += 1

					if not i in self.maskTag:
						GL.glColor4f(color[0], color[1], color[2], color[3])
						GL.glLoadIdentity()
						GL.glLoadMatrixf(self.camera.transpose(self.camera.getMVP()))						
						self.renderText(x, y, z, pt.GetLabel(), QtGui.QFont('Arial', 10, QtGui.QFont.Bold, False))
						GL.glLoadIdentity()
					
			GL.glPointSize(self.screen.parameterDialog.getPointSize())
			GL.glLineWidth(self.screen.parameterDialog.getTrajectoryWidth())
			
			GL.glEnable(GL.GL_LINE_SMOOTH)
			GL.glEnable(GL.GL_DEPTH_TEST)
			self.openGLDraw(self.markerShader, GL.GL_POINTS, vertexBuffer, colorBuffer)
			self.openGLDrawMultiArray(self.markerShader, GL.GL_LINE_STRIP, trajVertexBuffer, trajVertexStart, trajVertexCount, trajColorBuffer)
			
			
	def drawGroups(self):
		if self.frameData and self.screen.parameterDialog.getGroupLinkWidth() > 0:
			vertexBuffer = []
			vertexStart = []
			vertexCount = []
			colorBuffer = []
			
			maxVal = self.screen.data.getMaxDataValue()
			for group in self.groups:
				for link in group:
					pt1 = self.frameData.GetItem(link[0])
					color1 = (1, 1, 1, 1)
					
					colorBuffer.append(color1[0])
					colorBuffer.append(color1[1])
					colorBuffer.append(color1[2])
					colorBuffer.append(color1[3])					
					
					x1 = pt1.GetValue(self.currentFrame, 0) / maxVal
					y1 = pt1.GetValue(self.currentFrame, 1) / maxVal
					z1 = pt1.GetValue(self.currentFrame, 2) / maxVal
					vertexBuffer.append(x1)
					vertexBuffer.append(y1)
					vertexBuffer.append(z1)
					
					pt2 = self.frameData.GetItem(link[1])
					color2 = (1, 1, 1, 1)
					
					colorBuffer.append(color2[0])
					colorBuffer.append(color2[1])
					colorBuffer.append(color2[2])
					colorBuffer.append(color2[3])					
					
					x2 = pt2.GetValue(self.currentFrame, 0) / maxVal
					y2 = pt2.GetValue(self.currentFrame, 1) / maxVal
					z2 = pt2.GetValue(self.currentFrame, 2) / maxVal
					vertexBuffer.append(x2)
					vertexBuffer.append(y2)
					vertexBuffer.append(z2)
				
				if len(vertexStart) == 0:	
					vertexStart.append(0)
				else:
					vertexStart.append(vertexStart[-1] + vertexCount[-1])
				vertexCount.append(len(group) * 2)
					
			GL.glLineWidth(self.screen.parameterDialog.getGroupLinkWidth())
			GL.glEnable(GL.GL_LINE_SMOOTH)
			GL.glEnable(GL.GL_DEPTH_TEST)
			self.openGLDrawMultiArray(self.markerShader, GL.GL_LINES, vertexBuffer, vertexStart, vertexCount, colorBuffer)
			
			
	def openGLDraw(self, shader, primitive, vertex, color):
		vertexBuffer = numpy.array(vertex, numpy.float32)
		colorBuffer = numpy.array(color, numpy.float32)
		
		GL.glUseProgram(shader)
		mvpID = GL.glGetUniformLocation(shader, 'mvp')
		GL.glUniformMatrix4fv(mvpID, 1, GL.GL_TRUE, self.camera.getMVP())
		
		posID = GL.glGetAttribLocation(shader, 'pos')
		colorID = GL.glGetAttribLocation(shader, 'vertex_color')
		GL.glEnableVertexAttribArray(posID)
		GL.glEnableVertexAttribArray(colorID)
		
		GL.glVertexAttribPointer(posID,
								 3,
								 GL.GL_FLOAT,
								 GL.GL_FALSE,
								 0,
								 vertexBuffer)
		GL.glVertexAttribPointer(colorID,
								 4,
								 GL.GL_FLOAT,
								 GL.GL_FALSE,
								 0,
								 colorBuffer)				
		GL.glDrawArrays(primitive, 0, len(vertex))
		
		GL.glDisableVertexAttribArray(posID)
		GL.glDisableVertexAttribArray(colorID)
		GL.glUseProgram(0)
		
		
	def openGLDrawMultiArray(self, shader, primitive, vertex, start, count, color):
		vertexBuffer = numpy.array(vertex, numpy.float32)
		colorBuffer = numpy.array(color, numpy.float32)
		startBuffer = numpy.array(start, numpy.intc)
		countBuffer = numpy.array(count, numpy.intc)
		
		GL.glUseProgram(shader)
		mvpID = GL.glGetUniformLocation(shader, 'mvp')
		GL.glUniformMatrix4fv(mvpID, 1, GL.GL_TRUE, self.camera.getMVP())
		
		posID = GL.glGetAttribLocation(shader, 'pos')
		colorID = GL.glGetAttribLocation(shader, 'vertex_color')
		GL.glEnableVertexAttribArray(posID)
		GL.glEnableVertexAttribArray(colorID)
		
		GL.glVertexAttribPointer(posID,
								 3,
								 GL.GL_FLOAT,
								 GL.GL_FALSE,
								 0,
								 vertexBuffer)
		GL.glVertexAttribPointer(colorID,
								 4,
								 GL.GL_FLOAT,
								 GL.GL_FALSE,
								 0,
								 colorBuffer)				
		GL.glMultiDrawArrays(primitive, startBuffer, countBuffer, len(count))
		
		GL.glDisableVertexAttribArray(posID)
		GL.glDisableVertexAttribArray(colorID)
		GL.glUseProgram(0)
		
		
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Control:
			self.ctrlPressed = True
		if event.key() == QtCore.Qt.Key_Shift:
			self.shiftPressed = True
			
			
	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Control:
			self.ctrlPressed = False
		if event.key() == QtCore.Qt.Key_Shift:
			self.shiftPressed = False
		
		
	def mousePressEvent(self, event):
		self.lastPos = event.pos()
		self.mouseMoved = False
		
			
	def mouseReleaseEvent(self, event):
		if self.shiftPressed and self.mouseMoved and event.button() == QtCore.Qt.LeftButton:
			self.mousePickRect(self.lastPos, event.pos(), self.ctrlPressed)			
		if not self.mouseMoved and event.button() == QtCore.Qt.LeftButton:
			self.mousePick(event.pos(), self.ctrlPressed)			
		elif not self.mouseMoved and event.button() == QtCore.Qt.MiddleButton:
			self.screen.data.togglePaused()

		self.mouseRect = []
			
			
	def mouseMoveEvent(self, event):
		if len(self.mouseRect) > 0 and not self.shiftPressed:
			self.mouseRect = []
			self.lastPos = event.pos()

		dx = event.x() - self.lastPos.x()
		dy = event.y() - self.lastPos.y()
		
		self.mouseMoved = True		

		if event.buttons() & QtCore.Qt.LeftButton and not self.autoCam and not self.shiftPressed:
			self.yRot += dy
			self.zRot += dx
			self.camera.setRotY(self.yRot / 16)
			self.camera.setRotZ(self.zRot / 16)
		elif event.buttons() & QtCore.Qt.LeftButton and not self.autoCam and self.shiftPressed:
			self.mouseRect = [self.lastPos, event.pos()]
		elif event.buttons() & QtCore.Qt.MiddleButton and not self.autoCam and not self.shiftPressed:
			self.xTrans += dx
			self.zTrans -= dy
			self.camera.setTransX(self.xTrans * 0.01)
			self.camera.setTransZ(self.zTrans * 0.01)
		elif event.buttons() & QtCore.Qt.RightButton and not self.autoCam and not self.shiftPressed:
			self.yTrans += dy
			self.camera.setTransY(self.yTrans * 0.01)

		if not self.shiftPressed:
			self.lastPos = event.pos()		
		
		
	def wheelEvent(self, event):
		self.screen.data.offsetCurrentFrame(numpy.sign(event.delta()) * int(self.screen.parameterDialog.getScrollSpeed()))
		
		
	def mousePickRect(self, pos1, pos2, append):
		if self.frameData:
			rect = [numpy.min([pos1.x(), pos2.x()]), numpy.min([pos1.y(), pos2.y()]), numpy.max([pos1.x(), pos2.x()]), numpy.max([pos1.y(), pos2.y()])]
			
			tv = math.tan(self.camera.toRadian(self.screen.parameterDialog.getVerticalFOV()) * 0.5)
			th = math.tan(self.camera.toRadian(self.screen.parameterDialog.getHorizontalFOV()) * 0.5)
			viewport_width = self.width()
			viewport_height = viewport_width * (tv / th)
			
			pTopLeft = [(rect[0] - viewport_width * 0.5) / (viewport_width * 0.5), -(rect[1] - self.height() * 0.5) / (viewport_height * 0.5)]
			pTopRight = [(rect[2] - viewport_width * 0.5) / (viewport_width * 0.5), -(rect[1] - self.height() * 0.5) / (viewport_height * 0.5)]
			pBottomLeft = [(rect[0] - viewport_width * 0.5) / (viewport_width * 0.5), -(rect[3] - self.height() * 0.5) / (viewport_height * 0.5)]
			pBottomRight = [(rect[2] - viewport_width * 0.5) / (viewport_width * 0.5), -(rect[3] - self.height() * 0.5) / (viewport_height * 0.5)]
			
			rayTopLeft1 = self.camera.inverseProj(pTopLeft[0], pTopLeft[1], -1.0)
			rayTopLeft2 = self.camera.inverseProj(pTopLeft[0], pTopLeft[1], 1.0)
			rayTopRight1 = self.camera.inverseProj(pTopRight[0], pTopRight[1], -1.0)
			rayTopRight2 = self.camera.inverseProj(pTopRight[0], pTopRight[1], 1.0)
			rayBottomLeft1 = self.camera.inverseProj(pBottomLeft[0], pBottomLeft[1], -1.0)
			rayBottomLeft2 = self.camera.inverseProj(pBottomLeft[0], pBottomLeft[1], 1.0)
			rayBottomRight1 = self.camera.inverseProj(pBottomRight[0], pBottomRight[1], -1.0)
			rayBottomRight2 = self.camera.inverseProj(pBottomRight[0], pBottomRight[1], 1.0)
			
			if not append:
				self.selectedMarkers.clear()
			max = self.screen.data.getMaxDataValue()
			for i in range(self.frameData.GetItemNumber()):
				pt = self.frameData.GetItem(i)
				v = [pt.GetValue(self.currentFrame, 0) / max, pt.GetValue(self.currentFrame, 1) / max, pt.GetValue(self.currentFrame, 2) / max]
				vProj = self.camera.multiplyMatByVec(self.camera.mvp, v)
				vProj = [vProj[0] / vProj[3], vProj[1] / vProj[3], vProj[2] / vProj[3]]
				if vProj[0] > pTopLeft[0] and vProj[0] < pTopRight[0] and vProj[1] < pTopLeft[1] and vProj[1] > pBottomLeft[1]:
					if i in self.selectedMarkers:
						self.selectedMarkers.remove(i)
					else:
						self.selectedMarkers.add(i)
						
			self.screen.itemList.clearPick()
			for markerIndex in self.selectedMarkers:
				modelIndex = self.screen.itemList.model().index(markerIndex, 0, parent=self.screen.itemList.getRootMarkerIndex())
				item = self.screen.itemList.itemFromIndex(modelIndex)
				item.setTextColor(0, QtGui.QColor(0, 180, 50, 150))
				self.screen.itemList.setItemSelected(item, True)
		
		
	def mousePick(self, pos, append):
		if self.frameData:
			x = pos.x()
			y = pos.y()
			
			tv = math.tan(self.camera.toRadian(self.screen.parameterDialog.getVerticalFOV()) * 0.5)
			th = math.tan(self.camera.toRadian(self.screen.parameterDialog.getHorizontalFOV()) * 0.5)
			viewport_width = self.width()
			viewport_height = viewport_width * (tv / th)
			x = (x - viewport_width * 0.5) / (viewport_width * 0.5)
			y = -(y - self.height() * 0.5) / (viewport_height * 0.5)
			l1 = self.camera.inverseProj(x, y, -1.0)
			l2 = self.camera.inverseProj(x, y, 1.0)

			bestPick = [10000, -1, 10000]
			max = self.screen.data.getMaxDataValue()
			for i in range(self.frameData.GetItemNumber()):
				pt = self.frameData.GetItem(i)
				v = [pt.GetValue(self.currentFrame, 0) / max, pt.GetValue(self.currentFrame, 1) / max, pt.GetValue(self.currentFrame, 2) / max]
				vecLine = [l2[0] - l1[0], l2[1] - l1[1], l2[2] - l1[2]]
				vecPoint = [v[0] - l1[0], v[1] - l1[1], v[2] - l1[2]]
				length = self.camera.dot(vecLine, vecPoint) / math.sqrt(self.camera.length2(vecLine))
				uVecLine = self.camera.normalizeVec(vecLine)
				vecClosest = [l1[0] + uVecLine[0] * length, l1[1] + uVecLine[1] * length, l1[2] + uVecLine[2] * length]
				dist = math.sqrt(self.camera.length2([v[0] - vecClosest[0], v[1] - vecClosest[1], v[2] - vecClosest[2]]))
				
				cameraDist = math.sqrt(self.camera.length2([uVecLine[0] * length, uVecLine[1] * length, uVecLine[2] * length]))
				if dist < 0.01 and cameraDist < bestPick[2]:
					bestPick[0] = dist
					bestPick[1] = i
					bestPick[2] = cameraDist
			
			if not append:
				self.selectedMarkers.clear()
			if bestPick[1] != -1:
				if bestPick[1] in self.selectedMarkers:
					self.selectedMarkers.remove(bestPick[1])
				else:
					self.selectedMarkers.add(bestPick[1])
					
			self.screen.itemList.clearPick()
			for markerIndex in self.selectedMarkers:
				modelIndex = self.screen.itemList.model().index(markerIndex, 0, parent=self.screen.itemList.getRootMarkerIndex())
				item = self.screen.itemList.itemFromIndex(modelIndex)
				item.setTextColor(0, QtGui.QColor(0, 180, 50, 150))
				self.screen.itemList.setItemSelected(item, True)
					
					
	def itemListPick(self):
		self.selectedMarkers.clear()
		for item in self.screen.itemList.selectedItems():
			markerIndex = self.screen.itemList.indexFromItem(item).row()
			self.selectedMarkers.add(markerIndex)
			
			
	def clearItemConfig(self):
		self.maskDraw.clear()
		for i in range(self.screen.data.totalPoint):
			self.maskTraj.add(i)
			self.maskTag.add(i)
		self.colorDict.clear()
		
		self.groups = []
			
			
	def itemConfigChanged(self, item):
		index = item[0].row()
		parentIndex = item[0].parent().row()
		configType = item[1]
		if parentIndex == 0:
			if configType == 'draw':
				if item[2] == 2:
					if index in self.maskDraw:
						self.maskDraw.remove(index)
				elif item[2] == 0:
					self.maskDraw.add(index)				
			elif configType == 'traj':
				if item[2] == 2:
					if index in self.maskTraj:
						self.maskTraj.remove(index)
				elif item[2] == 0:
					self.maskTraj.add(index)
			elif configType == 'tag':
				if item[2] == 2:
					if index in self.maskTag:
						self.maskTag.remove(index)
				elif item[2] == 0:
					self.maskTag.add(index)
			elif configType == 'color':
				self.colorDict[index] = item[2]
		
		
	def updateTimer(self):
		self.currentFrame = self.screen.data.getCurrentFrame()
		self.frameData = self.screen.data.getCurrentFrameData()
		self.update()