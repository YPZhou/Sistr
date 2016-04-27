import numpy, math

class Camera():
	
	def __init__(self):
		self.rotY = 0
		self.rotZ = 0
		self.transX = 0
		self.transY = 0
		self.transZ = 0
		
		self.camPos = (0, 0, -1)
		self.targetPos = (0, 0, 0)
		self.fovH = 115
		self.fovV = 60
		self.near = 0.00001
		self.far = 1000
		
		self.ortho = False
		self.mvp = None
		self.changed = True
		
	def setRotY(self, rotY):
		if self.rotY != rotY:
			self.rotY = rotY
			self.changed = True
			
	def setRotZ(self, rotZ):
		if self.rotZ != rotZ:
			self.rotZ = rotZ
			self.changed = True
			
	def setTransX(self, transX):
		if self.transX != transX:
			self.transX = transX
			self.changed = True
			
	def setTransY(self, transY):
		if self.transY != transY:
			self.transY = transY
			self.changed = True
			
	def setTransZ(self, transZ):
		if self.transZ != transZ:
			self.transZ = transZ
			self.changed = True
			
	def setCamPos(self, camPos):
		if self.camPos != camPos:
			self.camPos = camPos
			self.changed = True
			
	def setTargetPos(self, targetPos):
		if self.targetPos != targetPos:
			self.targetPos = targetPos
			self.changed = True

	def setFovH(self, fovH):
		if self.fovH != fovH:
			self.fovH = fovH
			self.changed = True
			
	def setFovV(self, fovV):
		if self.fovV != fovV:
			self.fovV = fovV
			self.changed = True
			
	def setNear(self, near):
		if self.near != near:
			self.near = near
			self.changed = True

	def setFar(self, far):
		if self.far != far:
			self.far = far
			self.changed = True
			
	def setOrtho(self, ortho):
		if self.ortho != ortho:
			self.ortho = ortho
			self.changed = True
			
	def getMVP(self):
		if self.changed:
				
			# Rotation quaternion for rotY and rotZ
			qY = self.quaternion((1, 0, 0), -self.rotY)
			qZ = self.quaternion((0, 1, 0), self.rotZ)
			qRot = self.normalize(self.multiplyQuat(qY, qZ))
			
			# Transform quaternion to rotation matrix
			rotMat = self.matrixFromQuat(qRot)
			
			# change base for lookat direction
			vec = self.normalizeVec((self.camPos[0] - self.targetPos[0], self.camPos[1] - self.targetPos[1], self.camPos[2] - self.targetPos[2]))
			viewMat = self.lookat(vec, (0, 1, 0))
			
			# Translation matrices for model and view, equivalent to :
			#   modelTransMat = self.matrixFromTrans((-self.transX, -self.transY, self.transZ))
			#   viewTransMat = self.matrixFromTrans((-self.camPos[0], -self.camPos[1], -self.camPos[2]))
			#   transMat = self.multiplyMatrix(viewTransMat, modelTransMat)
			transMat = self.matrixFromTrans((-self.camPos[0] - self.transX, -self.camPos[1] - self.transY, -self.camPos[2] - self.transZ))
			
			# Calculate model-view matrix
			# Transformation order : viewMat -> transMat(viewTransMat -> modelTransMat) -> rotMat -> vertex
			# Rotation should be applied before translation for model matrix
			# Rotation should be applied after translation for view matrix
			# In normal camera mode, 'viewMat' is an identity matrix and in first person camera mode, 'rotMat' is an identity matrix
			modelViewMat = self.multiplyMatrix(viewMat, self.multiplyMatrix(transMat, rotMat))
			
			# Multiply projection matrix to the left
			if self.ortho:
				self.mvp = numpy.array(self.multiplyMatrix(self.orthographic(self.fovH, self.fovV, self.near, self.far), modelViewMat), numpy.float32)
			else:
				self.mvp = numpy.array(self.multiplyMatrix(self.perspective(self.fovH, self.fovV, self.near, self.far), modelViewMat), numpy.float32)
			
			# MVP updated
			self.changed = False
		return self.mvp
		
	# Converts angle from degree to radian	
	def toRadian(self, angle):
		return angle / 180.0 * math.pi
		
	# Reimplement of gluLookAt	
	def lookat(self, vec, up):
		z = self.normalizeVec(vec)
		y = up
		x = self.cross(y, z)
		y = self.cross(z, x)
		x = self.normalizeVec(x)
		y = self.normalizeVec(y)
		return (x[0], x[1], x[2], 0,
				y[0], y[1], y[2], 0,
				z[0], z[1], z[2], 0,
				0, 0, 0, 1)
	
	# Constructs a quaternion from a rotation of degree 'angle' around vector 'axis'
	def quaternion(self, axis, angle):
		angle *= 0.5
		sinAngle = math.sin(self.toRadian(angle))
		return self.normalize((axis[0] * sinAngle, axis[1] * sinAngle, axis[2] * sinAngle, math.cos(self.toRadian(angle))))
		
	# Normalizes quaternion 'q'
	def normalize(self, q):
		length = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])
		return (q[0] / length, q[1] / length, q[2] / length, q[3] / length)
		
	# Multiplies 2 quaternions : 'q1' * 'q2'	
	def multiplyQuat(self, q1, q2):
		return (q1[3] * q2[0] + q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1],
				q1[3] * q2[1] + q1[1] * q2[3] + q1[2] * q2[0] - q1[0] * q2[2],
				q1[3] * q2[2] + q1[2] * q2[3] + q1[0] * q2[1] - q1[1] * q2[0],
				q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2])
	
	# Multiplies matrix 'm' by vector 'v'
	def multiplyMatByVec(self, m, v):
		w = 1.0
		if len(v) == 4:
			w = v[3]
		return (m[0] * v[0] + m[1] * v[1] + m[2] * v[2] + m[3] * w,
				m[4] * v[0] + m[5] * v[1] + m[6] * v[2] + m[7] * w,
				m[8] * v[0] + m[9] * v[1] + m[10] * v[2] + m[11] * w,
				m[12] * v[0] + m[13] * v[1] + m[14] * v[2] + m[15] * w)
				
	# Multiplies 2 Mat4 : 'm1' * 'm2'			
	def multiplyMatrix(self, m1, m2):
		res = []
		for i in range(0, 4):
			for j in range(0, 4):
				res.append(m1[i * 4] * m2[j] + m1[i * 4 + 1] * m2[j + 4] + m1[i * 4 + 2] * m2[j + 8] + m1[i * 4 + 3] * m2[j + 12])
		return res
	
	# Converts quaternion 'q' to a rotation matrix
	def matrixFromQuat(self, q):
		x2 = q[0] * q[0]
		y2 = q[1] * q[1]
		z2 = q[2] * q[2]
		xy = q[0] * q[1]
		xz = q[0] * q[2]
		yz = q[1] * q[2]
		wx = q[3] * q[0]
		wy = q[3] * q[1]
		wz = q[3] * q[2]
		return (1.0 - 2.0 * (y2 + z2), 2.0 * (xy - wz), 2.0 * (xz + wy), 0.0,
				2.0 * (xy + wz), 1.0 - 2.0 * (x2 + z2), 2.0 * (yz - wx), 0.0,
				2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (x2 + y2), 0.0,
				0.0, 0.0, 0.0, 1.0)
		
	# Constructs a translation matrix
	def matrixFromTrans(self, trans):
		return (1, 0, 0, trans[0],
				0, 1, 0, trans[1],
				0, 0, 1, trans[2],
				0, 0, 0, 1)
		
	# Constructs a perspective projection matrix
	def perspective(self, fovH, fovV, near, far):
		r = math.tan(self.toRadian(fovH * 0.5))
		t = math.tan(self.toRadian(fovV * 0.5))
		return (1 / r, 0, 0, 0,
				0, 1 / t, 0, 0,
				0, 0, -(far + near) / (far - near), -(2 * far * near) / (far - near),
				0, 0, -1, 0)
	
	# Constructs an orthographic projection matrix
	def orthographic(self, fovH, fovV, near, far):
		r = math.tan(self.toRadian(fovH * 0.5))
		t = math.tan(self.toRadian(fovV * 0.5))
		return (1 / r, 0, 0, 0,
				0, 1 / t, 0, 0,
				0, 0, -2 / (far - near), -(far + near) / (far - near),
				0, 0, 0, 1)
				
	# Inverse project 2D mouse position to world space
	# Mouse position should be normalized to [-1, 1]
	# Return vector unchanged if transformation matrix is not invertible
	def inverseProj(self, mouseX, mouseY, z):
		# Rotation quaternion for rotY and rotZ
		qY = self.quaternion((1, 0, 0), -self.rotY)
		qZ = self.quaternion((0, 1, 0), self.rotZ)
		qRot = self.normalize(self.multiplyQuat(qY, qZ))
		
		# Transform quaternion to rotation matrix
		rotMat = self.matrixFromQuat(qRot)
		
		# change base for lookat direction
		vec = self.normalizeVec((self.camPos[0] - self.targetPos[0], self.camPos[1] - self.targetPos[1], self.camPos[2] - self.targetPos[2]))
		viewMat = self.lookat(vec, (0, 1, 0))
		
		# Translation matrices for model and view, equivalent to :
		#   modelTransMat = self.matrixFromTrans((-self.transX, -self.transY, self.transZ))
		#   viewTransMat = self.matrixFromTrans((-self.camPos[0], -self.camPos[1], -self.camPos[2]))
		#   transMat = self.multiplyMatrix(viewTransMat, modelTransMat)
		transMat = self.matrixFromTrans((-self.camPos[0] - self.transX, -self.camPos[1] - self.transY, -self.camPos[2] - self.transZ))
		
		# Calculate model-view matrix
		# Transformation order : viewMat -> transMat(viewTransMat -> modelTransMat) -> rotMat -> vertex
		# Rotation should be applied before translation for model matrix
		# Rotation should be applied after translation for view matrix
		# In normal camera mode, 'viewMat' is an identity matrix and in first person camera mode, 'rotMat' is an identity matrix
		modelViewMat = self.multiplyMatrix(viewMat, self.multiplyMatrix(transMat, rotMat))
		
		# Multiply projection matrix to the left
		if self.ortho:
			mvp = numpy.array(self.multiplyMatrix(self.orthographic(self.fovH, self.fovV, self.near, self.far), modelViewMat), numpy.float32)
		else:
			mvp = numpy.array(self.multiplyMatrix(self.perspective(self.fovH, self.fovV, self.near, self.far), modelViewMat), numpy.float32)
			
		unprojMat = self.invertMatrix(mvp)
		if unprojMat != None:
			unproj = self.multiplyMatByVec(unprojMat, (mouseX, mouseY, z, 1.0))
			if unproj[3] != 0:
				return (unproj[0] / unproj[3], unproj[1] / unproj[3], unproj[2] / unproj[3])
		return (mouseX, mouseY, z)
				
	# Transposes matrix 'm'
	def transpose(self, m):
		return (m[0], m[4], m[8], m[12],
				m[1], m[5], m[9], m[13],
				m[2], m[6], m[10], m[14],
				m[3], m[7], m[11], m[15])
				
	# Calculates inverse of matrix m
	# Reimplement of gluInvertMatrix
	def invertMatrix(self, m):
		inv = []
		inv.append(m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] + m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10])
		inv.append(-m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] - m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10])
		inv.append(m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] + m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6])
		inv.append(-m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] - m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6])
		inv.append(-m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] - m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10])
		inv.append(m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] + m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10])
		inv.append(-m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] - m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6])
		inv.append(m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] + m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6])
		inv.append(m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] + m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9])
		inv.append(-m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] - m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9])
		inv.append(m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] + m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5])
		inv.append(-m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] - m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5])
		inv.append(-m[4] * m[9] * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] - m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9])
		inv.append(m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] + m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9])
		inv.append(-m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] - m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5])
		inv.append(m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] + m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5])
		
		det = m[0] * inv[0] + m[1] * inv[4] + m[2] * inv[8] + m[3] * inv[12]
		if det == 0:
			return None
		
		det = 1.0 / det
		mOut = []
		for i in range(16):
			mOut.append(inv[i] * det)
		return mOut
		
	# Calculates length^2 of vector 'v'	
	def length2(self, v):
		return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]
		
	# Calculates vector dot product : 'v1' * 'v2'	
	def dot(self, v1, v2):
		return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
		
	# Calculates vector cross product : 'v1' x 'v2'
	def cross(self, v1, v2):
		return (v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0])
		
	# Normalizes vector 'v'
	def normalizeVec(self, v):
		l2 = self.length2(v)
		if l2 == 0:
			return (0, 0, 0)
		l = math.sqrt(l2)
		return (v[0] / l, v[1] / l, v[2] / l)