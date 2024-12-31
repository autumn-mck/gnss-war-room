from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from misc import saveToTempFile
from mqtt import GnssData
from stats.generate import generateStats

class MiscStatsWindow(QMainWindow):
	"""Window for displaying miscellaneous statistics"""

	satelliteReceivedEvent = pyqtSignal()
	def __init__(self, palette):
		super().__init__()
		self.setWindowTitle("Misc Stats")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette

		self.satelliteReceivedEvent.connect(self.updateWithNewData)
		self.latestData = None

		self.svgFont = Font()
		svgStr, width, height = makeSvgString(self.svgFont,
			"Waiting for data...".encode('ascii'),
			fontThickness=2, fontColour=palette.foreground)
		svgFile = saveToTempFile(svgStr)
		self.svg = QSvgWidget(svgFile, parent=self)
		self.svg.setGeometry(0, 0, width, height)

		self.setGeometry(0, 0, 500, 500)
		self.show()

	def onNewData(self, gnssData: GnssData):
		"""Update window with new data"""
		self.latestData = gnssData
		self.satelliteReceivedEvent.emit()

	def updateWithNewData(self):
		"""Update the misc stats window with new data"""
		if self.latestData is None:
			return
		svgStr, width, height = generateStats(self.latestData, self.customPalette, self.svgFont)
		svgFile = saveToTempFile(svgStr)

		width /= 2
		height /= 2
		self.svg.load(svgFile)
		self.svg.setGeometry(0, 0, int(width), int(height))
