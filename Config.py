# == ATTENTION ==
# For 3D models, use "meter" as length unit
# For vicon data, use "millimeter" as length unit
#
# In the MODEL_FILES list, put only the names of the obj file
# mtl and texture files will be loaded automatically if the references are correct
#
# In the REFERENCE_MARKERS list, put the names of markers that the models should follow
# Put an empty string if the model should be static
#
# Translation is in meter
# Rotation is in degree
# ===============
# MODEL_PATH			= ''
# MODEL_FILES			= ['cube.obj', 'boxScene.obj']
# REFERENCE_MARKERS	= ['EyeVector_in_Viconrf', '']
# MODEL_TRANSLATIONS	= [(0, 0, 0), (0, 0, 2.25)]
# MODEL_ROTATIONS		= [(0, 0, 0), (0, 90, 0)]
# DRAW_MODEL			= True

# SCREEN_SIZE = [1920, 1000]

VERTICAL_FOV		= 60
HORIZONTAL_FOV		= 90
NEAR_PLANE			= 0.01
FAR_PLANE			= 1000
POINT_SIZE			= 3
SEGMENT_WIDTH		= 3
CONE_ANGLE			= 10
CONE_TRANSPARENCY	= 0.2
GRID_LINE_COUNT		= 10
GRID_WIDTH			= 0.5
GRID_SPACING		= 500
GRID_VISIBILITY		= True
AXIS_WIDTH			= 1
AXIS_VISIBILITY		= True
TRAJECTORY_WIDTH	= 0.7
TRAJECTORY_LENGTH	= 50
SCROLL_SPEED		= 1

# SEGMENTS = []
# CONES = [['EyePosition_in_Viconrf', 'EyeVector_in_Viconrf']]
# MASK_3D = []
# MASK_2D = []