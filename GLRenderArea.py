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
	
		self.xRot = 0.0
		self.yRot = 0.0
		self.zRot = 0.0
		
		self.xTrans = 0.0
		self.yTrans = 0.0
		self.zTrans = 0.0
		
		self.lastPos = QtCore.QPoint()
		
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
		
		self.selectedMarkers = set([])
		
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
		# self.drawSegments()
		# self.drawCones()
		self.drawMarkers()
		
		GL.glDisable(GL.GL_CULL_FACE)
		GL.glDisable(GL.GL_DEPTH_TEST)
		
		self.openGLDraw(self.shader, GL.GL_LINES, self.testVertexBuffer, self.testColorBuffer)
		
		painter = QtGui.QPainter(self)
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
			self.camera.setCamPos((0, 0, -1))
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
			vertexBuffer.append((0, 0, -max))
			vertexBuffer.append((0, 0, max))
			for i in numpy.arange(spacing, max + spacing * 0.5, spacing):
				vertexBuffer.append((-max, 0, i))
				vertexBuffer.append((max, 0, i))
				vertexBuffer.append((-max, 0, -i))
				vertexBuffer.append((max, 0, -i))
			
				vertexBuffer.append((i, 0, -max))
				vertexBuffer.append((i, 0, max))
				vertexBuffer.append((-i, 0, -max))
				vertexBuffer.append((-i, 0, max))
				
			colorBuffer = numpy.empty(len(vertexBuffer) * 4)
			colorBuffer.fill(0.6)
			
			GL.glLineWidth (self.screen.parameterDialog.getGridWidth())
			self.openGLDraw(self.shader, GL.GL_LINES, vertexBuffer, colorBuffer)	
		
		if self.screen.parameterDialog.getAxisVisibility():
			vertexBuffer = []
			vertexBuffer.append((0, 0, 0))
			vertexBuffer.append((max, 0, 0))
			vertexBuffer.append((0, 0, 0))
			vertexBuffer.append((0, 0, -max))
			vertexBuffer.append((0, 0, 0))
			vertexBuffer.append((0, max, 0))
			
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
			
			max = self.screen.data.getMaxDataValue()
			for i in range(self.frameData.GetItemNumber()):
				pt = self.frameData.GetItem(i)
				color = (1, 1, 1, 1)
				if i in self.selectedMarkers:
					color = (0.2, 0.2, 0.8, 1)
				
				colorBuffer.append(color[0])
				colorBuffer.append(color[1])
				colorBuffer.append(color[2])
				colorBuffer.append(color[3])
				
				
				x = pt.GetValue(self.currentFrame, 0) / max
				z = -pt.GetValue(self.currentFrame, 1) / max
				y = pt.GetValue(self.currentFrame, 2) / max
				vertexBuffer.append(x)
				vertexBuffer.append(y)
				vertexBuffer.append(z)
				
				# print x, y, z
				
				# if not pt in self.screen.mask3D and not numpy.isnan(self.syncTimer.viconData.getValueGLRender(self.currentFrame, pt + ':X')):
				# 	if pt in self.screen.colorDict:
				# 		color = (self.screen.colorDict[pt].redF(), self.screen.colorDict[pt].greenF(), self.screen.colorDict[pt].blueF(), self.screen.colorDict[pt].alphaF())
				# 	else:
				# 		color = (1, 1, 1, 0.7)
				# 	colorBuffer.append(color[0])
				# 	colorBuffer.append(color[1])
				# 	colorBuffer.append(color[2])
				# 	colorBuffer.append(color[3])
						
				# 	x, y, z = self.syncTimer.viconData.getValueGLRender(self.currentFrame, pt + ':Y'), self.syncTimer.viconData.getValueGLRender(self.currentFrame, pt + ':Z'), self.syncTimer.viconData.getValueGLRender(self.currentFrame, pt + ':X')
				# 	vertexBuffer.append(x)
				# 	vertexBuffer.append(y)
				# 	vertexBuffer.append(z)
					
					# if not pt in self.screen.maskTraj and self.parameterDialog.getTrajectoryWidth() > 0:
					# 	trajX = self.syncTimer.viconData.getTrajectory(self.currentFrame, pt + ':Y', self.parameterDialog.getTrajectoryLength())
					# 	trajY = self.syncTimer.viconData.getTrajectory(self.currentFrame, pt + ':Z', self.parameterDialog.getTrajectoryLength())
					# 	trajZ = self.syncTimer.viconData.getTrajectory(self.currentFrame, pt + ':X', self.parameterDialog.getTrajectoryLength())
					# 	if len(trajVertexCount) != 0:
					# 		trajVertexStart.append(trajVertexStart[-1] + trajVertexCount[-1])
					# 	else:
					# 		trajVertexStart.append(0)
					# 	trajVertexCount.append(0)
					# 	for i in range(0, len(trajX)):
					# 		if not numpy.isnan(trajX[i]):
					# 			trajVertexBuffer.append(trajX[i])
					# 			trajVertexBuffer.append(trajY[i])
					# 			trajVertexBuffer.append(trajZ[i])
					# 			trajColorBuffer.append(color[0])
					# 			trajColorBuffer.append(color[1])
					# 			trajColorBuffer.append(color[2])
					# 			trajColorBuffer.append(color[3])
					# 			trajVertexCount[-1] += 1
					
					# if not pt in self.screen.maskTag:
					# 	GL.glLoadIdentity()
					# 	GL.glLoadMatrixf(self.camera.transpose(self.camera.getMVP()))						
					# 	self.renderText(x, y, z, pt, QtGui.QFont('Arial', 12, QtGui.QFont.Bold, False))
					# 	GL.glLoadIdentity()
			
			# vertexBuffer = numpy.array(vertexBuffer, numpy.float32)
			# colorBuffer = numpy.array(colorBuffer, numpy.float32)
					
			GL.glPointSize(self.screen.parameterDialog.getPointSize())
			# GL.glLineWidth(self.parameterDialog.getTrajectoryWidth())
			
			GL.glEnable(GL.GL_DEPTH_TEST)
			self.openGLDraw(self.markerShader, GL.GL_POINTS, vertexBuffer, colorBuffer)
			# GL.glUseProgram(self.shader)
			# mvpID = GL.glGetUniformLocation(self.shader, 'mvp')
			# GL.glUniformMatrix4fv(mvpID, 1, GL.GL_TRUE, self.camera.getMVP())
			
			# posID = GL.glGetAttribLocation(self.shader, 'pos')
			# colorID = GL.glGetAttribLocation(self.shader, 'vertex_color')
			# GL.glEnableVertexAttribArray(posID)
			# GL.glEnableVertexAttribArray(colorID)
			# GL.glVertexAttribPointer(posID,
			# 						 3,
			# 						 GL.GL_FLOAT,
			# 						 GL.GL_FALSE,
			# 						 0,
			# 						 vertexBuffer)
			# GL.glVertexAttribPointer(colorID,
			# 						 4,
			# 						 GL.GL_FLOAT,
			# 						 GL.GL_FALSE,
			# 						 0,
			# 						 colorBuffer)				
			# GL.glDrawArrays(GL.GL_POINTS, 0, len(vertexBuffer) / 3)
		
			# trajVertexBuffer = numpy.array(trajVertexBuffer, numpy.float32)
			# trajColorBuffer = numpy.array(trajColorBuffer, numpy.float32)
			# GL.glVertexAttribPointer(posID,
			# 						 3,
			# 						 GL.GL_FLOAT,
			# 						 GL.GL_FALSE,
			# 						 0,
			# 						 trajVertexBuffer)
			# GL.glVertexAttribPointer(colorID,
			# 						 4,
			# 						 GL.GL_FLOAT,
			# 						 GL.GL_FALSE,
			# 						 0,
			# 						 trajColorBuffer)									 
			# GL.glMultiDrawArrays(GL.GL_LINE_STRIP, numpy.array(trajVertexStart, numpy.intc), numpy.array(trajVertexCount, numpy.intc), len(trajVertexCount))
			
			# GL.glDisableVertexAttribArray(posID)
			# GL.glDisableVertexAttribArray(colorID)
			# GL.glUseProgram(0)
			
			
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
		GL.glDrawArrays(primitive, 0, len(vertexBuffer))
		
		GL.glDisableVertexAttribArray(posID)
		GL.glDisableVertexAttribArray(colorID)
		GL.glUseProgram(0)
		
		
	def mousePressEvent(self, event):
		self.lastPos = event.pos()
		self.mouseMoved = False
		
			
	def mouseReleaseEvent(self, event):
		if not self.mouseMoved and event.button() == QtCore.Qt.LeftButton:
			self.mousePick(event.pos())			
		elif not self.mouseMoved and event.button() == QtCore.Qt.MiddleButton:
			self.screen.data.togglePaused()
			
			
	def mouseMoveEvent(self, event):
		dx = event.x() - self.lastPos.x()
		dy = event.y() - self.lastPos.y()
		
		self.mouseMoved = True

		if event.buttons() & QtCore.Qt.LeftButton and not self.autoCam:
			self.yRot += dy
			self.zRot += dx
			self.camera.setRotY(self.yRot / 16)
			self.camera.setRotZ(self.zRot / 16)
		elif event.buttons() & QtCore.Qt.MiddleButton and not self.autoCam:
			self.xTrans += dx
			self.yTrans += dy
			self.camera.setTransX(self.xTrans * 0.01)
			self.camera.setTransY(self.yTrans * 0.01)
		elif event.buttons() & QtCore.Qt.RightButton and not self.autoCam:
			self.zTrans -= dy
			self.camera.setTransZ(self.zTrans * 0.01)

		self.lastPos = event.pos()
		
		
	def wheelEvent(self, event):
		self.screen.data.offsetCurrentFrame(numpy.sign(event.delta()) * int(self.screen.parameterDialog.getScrollSpeed()))
		
		
	def mousePick(self, pos):
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
			# l2 = self.camera.camPos
			
			self.testVertexBuffer.append(l1)
			self.testVertexBuffer.append(l2)
			
			for i in range(4):
				self.testColorBuffer.append([0.2, 0.8, 0.8, 1.0])
			for i in range(4):
				self.testColorBuffer.append([0.8, 0.2, 0.8, 1.0])

			bestPick = [10000, -1, 10000]
			max = self.screen.data.getMaxDataValue()
			for i in range(self.frameData.GetItemNumber()):
				pt = self.frameData.GetItem(i)
				v = [pt.GetValue(self.currentFrame, 0) / max, pt.GetValue(self.currentFrame, 2) / max, -pt.GetValue(self.currentFrame, 1) / max]
				vecLine = [l2[0] - l1[0], l2[1] - l1[1], l2[2] - l1[2]]
				vecPoint = [v[0] - l1[0], v[1] - l1[1], v[2] - l1[2]]
				length = self.camera.dot(vecLine, vecPoint) / math.sqrt(self.camera.length2(vecLine))
				uVecLine = self.camera.normalizeVec(vecLine)
				vecClosest = [l1[0] + uVecLine[0] * length, l1[1] + uVecLine[1] * length, l1[2] + uVecLine[2] * length]
				dist = self.camera.length2([vecPoint[0] - vecClosest[0], vecPoint[0] - vecClosest[0], vecPoint[0] - vecClosest[0]])
				cameraDist = self.camera.length2([v[0] - self.camera.camPos[0], v[1] - self.camera.camPos[1], v[1] - self.camera.camPos[1]])
				if dist < bestPick[0]:
					bestPick[0] = dist
					bestPick[1] = i
					bestPick[2] = cameraDist
			print bestPick
			self.selectedMarkers.clear()
			self.selectedMarkers.add(bestPick[1])
		
		
	def updateTimer(self):
		self.currentFrame = self.screen.data.getCurrentFrame()
		self.frameData = self.screen.data.getCurrentFrameData()
		self.update()