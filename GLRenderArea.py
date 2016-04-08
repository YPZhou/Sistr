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


class GLRenderArea(QtOpenGL.QGLWidget):

	def __init__(self, screen, fmt):	
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
		
		self.vw = 0
		self.vh = 0
		
		self.camera = Camera()
		self.screen = screen
				
		self.programCompiled = False
		
		# self.currentFrame = self.syncTimer.viconData.getFrameGLRender(0)
		# self.frame = self.syncTimer.frame
		# self.updateInterval = self.syncTimer.updateInterval
		# self.pause = self.syncTimer.pause
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
	
	def initializeGL(self):
		pass

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
			self.shader = shaders.compileProgram(self.vertexShader, self.fragmentShader)
			self.programCompiled = True
	
		GL.glShadeModel(GL.GL_FLAT)
		GL.glEnable(GL.GL_DEPTH_TEST)

		GL.glEnable(GL.GL_POINT_SMOOTH)
		GL.glHint(GL.GL_POINT_SMOOTH_HINT, GL.GL_NICEST)
		GL.glEnable(GL.GL_LINE_SMOOTH)
		GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
		GL.glEnable(GL.GL_BLEND)
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		
		# tv = math.tan(self.parameterDialog.getVerticalFOV() * 0.5 / 180 * math.pi)
		# th = math.tan(self.parameterDialog.getHorizontalFOV() * 0.5 / 180 * math.pi)
		tv = 1
		th = 1
		viewport_width = self.width()
		viewport_height = int(viewport_width * (tv / th))
		GL.glViewport((self.width() - viewport_width) / 2, (self.height() - viewport_height) / 2, viewport_width, viewport_height)
		
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		
		self.updateCamera()				
		self.drawCoords()		
		# self.drawSegments()
		# self.drawModels()
		# self.drawCones()
		# self.drawMarkers()
		
		GL.glDisable(GL.GL_CULL_FACE)
		GL.glDisable(GL.GL_DEPTH_TEST)
		
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
			
		# self.camera.setFovH(self.parameterDialog.getHorizontalFOV())
		self.camera.setFovH(60)
		# self.camera.setFovV(self.parameterDialog.getVerticalFOV())
		self.camera.setFovV(60)
		
	def drawCoords(self):
		GL.glDisable(GL.GL_DEPTH_TEST)
		max = 10.0
		# max = self.parameterDialog.getGridSpacing() / self.syncTimer.viconData.max3D * self.parameterDialog.getGridLineCount()
		# if self.parameterDialog.getGridVisibility() and self.parameterDialog.getGridWidth() > 0 and self.parameterDialog.getGridSpacing() > 0:
			# quadrillage sur le sol			
		vertexBuffer = []
		vertexBuffer.append((-max, 0, 0))
		vertexBuffer.append((max, 0, 0))
		vertexBuffer.append((0, 0, -max))
		vertexBuffer.append((0, 0, max))
		for i in numpy.arange(5 / max, max + 5 / max * 0.5, 5 / max):
			vertexBuffer.append((-max, 0, i))
			vertexBuffer.append((max, 0, i))
			vertexBuffer.append((-max, 0, -i))
			vertexBuffer.append((max, 0, -i))
		
			vertexBuffer.append((i, 0, -max))
			vertexBuffer.append((i, 0, max))
			vertexBuffer.append((-i, 0, -max))
			vertexBuffer.append((-i, 0, max))			
			
		# GL.glLineWidth (self.parameterDialog.getGridWidth())
		GL.glUseProgram(self.shader)
		mvpID = GL.glGetUniformLocation(self.shader, 'mvp')
		GL.glUniformMatrix4fv(mvpID, 1, GL.GL_TRUE, self.camera.getMVP())
		vertexBuffer = numpy.array(vertexBuffer, numpy.float32)
		colorBuffer = numpy.empty(len(vertexBuffer) * 4)
		colorBuffer.fill(0.6)
		
		# On OS X, attributes in GLSL shaders do not have default position,
		# we should always use glGetAttribLocation to retrieve their positions.
		posID = GL.glGetAttribLocation(self.shader, 'pos')
		colorID = GL.glGetAttribLocation(self.shader, 'vertex_color')
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
		GL.glEnableVertexAttribArray(posID)	
		GL.glEnableVertexAttribArray(colorID)			
		GL.glDrawArrays(GL.GL_LINES, 0, len(vertexBuffer))
		GL.glDisableVertexAttribArray(posID)
		GL.glDisableVertexAttribArray(colorID)
		GL.glUseProgram(0)
			
		# if self.parameterDialog.getAxisVisibility() and self.parameterDialog.getAxisWidth() > 0:
			# repere			
		vertexBuffer = []
		vertexBuffer.append((0, 0, 0))
		vertexBuffer.append((0, 0, max))
		vertexBuffer.append((0, 0, 0))
		vertexBuffer.append((max, 0, 0))
		vertexBuffer.append((0, 0, 0))
		vertexBuffer.append((0, max, 0))
		
		colorBuffer = []
		colorBuffer.append((1, 0, 0, 0.4))
		colorBuffer.append((1, 0, 0, 0.4))
		colorBuffer.append((0, 1, 0, 0.4))
		colorBuffer.append((0, 1, 0, 0.4))
		colorBuffer.append((0, 0, 1, 0.4))
		colorBuffer.append((0, 0, 1, 0.4))
		
		# GL.glLineWidth (self.parameterDialog.getAxisWidth())
		GL.glUseProgram(self.shader)
		mvpID = GL.glGetUniformLocation(self.shader, 'mvp')
		GL.glUniformMatrix4fv(mvpID, 1, GL.GL_TRUE, self.camera.getMVP())
		vertexBuffer = numpy.array(vertexBuffer, numpy.float32)
		colorBuffer = numpy.array(colorBuffer, numpy.float32)
		posID = GL.glGetAttribLocation(self.shader, 'pos')
		colorID = GL.glGetAttribLocation(self.shader, 'vertex_color')
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
		GL.glEnableVertexAttribArray(posID)	
		GL.glEnableVertexAttribArray(colorID)	
		GL.glDrawArrays(GL.GL_LINES, 0, len(vertexBuffer))
		GL.glDisableVertexAttribArray(posID)
		GL.glDisableVertexAttribArray(colorID)
		GL.glUseProgram(0)
	# GL.glEnable(GL.GL_DEPTH_TEST)
		
		
	def mousePressEvent(self, event):
		self.lastPos = event.pos()
		self.mouseMoved = False
		
			
	def mouseReleaseEvent(self, event):
		if not self.mouseMoved and event.button() == QtCore.Qt.MiddleButton:
			self.syncTimer.pause = not self.syncTimer.pause
			self.pause = self.syncTimer.pause
			
			
	def mouseMoveEvent(self, event):
		dx = event.x() - self.lastPos.x()
		dy = event.y() - self.lastPos.y()
		
		self.mouseMoved = True

		if event.buttons() & QtCore.Qt.LeftButton and not self.autoCam:
		# if event.buttons() & QtCore.Qt.LeftButton:
			self.yRot += dy
			self.zRot += dx
			self.camera.setRotY(self.yRot / 16)
			self.camera.setRotZ(self.zRot / 16)
		elif event.buttons() & QtCore.Qt.MiddleButton and not self.autoCam:
		# elif event.buttons() & QtCore.Qt.MiddleButton:
			self.xTrans += dx
			self.yTrans += dy
			self.camera.setTransX(self.xTrans * 0.01)
			self.camera.setTransY(self.yTrans * 0.01)
		elif event.buttons() & QtCore.Qt.RightButton and not self.autoCam:
		# elif event.buttons() & QtCore.Qt.RightButton:
			self.zTrans += dy
			self.camera.setTransZ(self.zTrans * 0.01)

		self.lastPos = event.pos()
		
		
	def wheelEvent(self, event):
		pass
		# self.syncTimer.frame += numpy.sign(event.delta()) * self.parameterDialog.getScrollSpeed()
		
		
	def updateTimer(self):
		# self.pause = self.syncTimer.pause
		# self.frame = self.syncTimer.frame
		# if self.frame >= self.syncTimer.viconData.frameCount:
		# 	self.frame = 0
		# self.currentFrame = self.syncTimer.viconData.getFrameGLRender(self.frame)
		self.update()
		# self.screen.centralTab.currentWidget().update()
		# self.screen.update()