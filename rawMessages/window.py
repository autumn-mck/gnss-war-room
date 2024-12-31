from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import pyqtSignal

from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from misc import saveToTempFile
from palettes.palette import Palette

class RawMessageWindow(QMainWindow):
	"""Window for displaying raw messages"""

	satelliteReceivedEvent = pyqtSignal()
	numMessagesToKeep = 20

	def __init__(self, palette: Palette):
		super().__init__()
		self.setWindowTitle("Raw Messages")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette

		self.messages = [b''] * self.numMessagesToKeep

		self.svgFont = Font()
		svgStr, width, height = makeSvgString(self.svgFont,
			"Waiting for data...".encode('ascii'),
			fontThickness=2,
			fontColour=palette.foreground)
		svgFile = saveToTempFile(svgStr)
		self.svg = QSvgWidget(svgFile, parent=self)
		self.svg.setGeometry(0, 0, width, height)

		self.satelliteReceivedEvent.connect(self.updateMessageLog)

		self.setGeometry(0, 0, 500, 500)
		self.show()

	def onNewData(self, message: bytes):
		"""Update the raw message window with new data"""
		self.messages.insert(0, message)
		self.messages.pop()
		self.satelliteReceivedEvent.emit()

	def updateMessageLog(self):
		"""Update the displayed message log"""
		strToDisplay = ""
		for message in self.messages:
			strToDisplay += message.decode('utf-8')
			strToDisplay += "\n\r"
		svgStr, width, height = makeSvgString(self.svgFont,
			strToDisplay.encode('ascii'),
			fontThickness=2,
			fontColour=self.customPalette.foreground)
		width /= 2.5
		height /= 2.5
		svgFile = saveToTempFile(svgStr)
		self.svg.load(svgFile)
		self.svg.setGeometry(0, 0, int(width), int(height))
