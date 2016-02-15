import sys
from PyQt4 import QtCore, QtGui

from Data import Data
from Screen import ScreenManager


def main():
	app = QtGui.QApplication(sys.argv)
	print 'Preparing main window'
	
	data = Data()
	screenManager = ScreenManager(data)
	sys.exit(app.exec_())

	
if __name__ == '__main__':
	main()