from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import pyqtSignal

from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from mapdata.maps import RawMessageConfig, saveToTempFile
from palettes.palette import Palette

class RawMessageWindow(QMainWindow):
	"""Window for displaying raw messages"""

	satelliteReceivedEvent = pyqtSignal()
	numMessagesToKeep = 20

	def __init__(self, palette: Palette, config: RawMessageConfig):
		super().__init__()
		self.setWindowTitle("Raw Messages")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette
		self.config = config

		self.messages = [b''] * self.numMessagesToKeep

		self.svgFont = Font("./font/01347-80012.bin")
		svgStr, width, height = makeSvgString(self.svgFont,
			"Waiting for data...".encode('ascii'),
			scale=2, border=4, offset=0, addGrid=False, drawShadow=False, fontThickness=1.4, fontColour="#ffffff")
		svgFile = saveToTempFile(svgStr)
		self.svg = QSvgWidget(svgFile, parent=self)
		self.svg.setGeometry(0, 0, width, height)

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.setGeometry(0, 0, 500, 500)
		self.show()

	def onNewData(self, message: bytes):
		"""Update the raw message window with new data"""
		if self.config.logToConsole:
			print(message.decode('utf-8'))
		self.messages.insert(0, message)
		self.messages.pop()
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		strToDisplay = ""
		for message in self.messages:
			strToDisplay += message.decode('utf-8')
			strToDisplay += "\n\r"
		svgStr, width, height = makeSvgString(self.svgFont,
			strToDisplay.encode('ascii'),
			scale=2, border=4, offset=0, addGrid=False, drawShadow=False, fontThickness=2, fontColour="#ffffff")
		width /= 2.5
		height /= 2.5
		svgFile = saveToTempFile(svgStr)
		self.svg.load(svgFile)
		self.svg.setGeometry(0, 0, int(width), int(height))