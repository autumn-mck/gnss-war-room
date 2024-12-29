from datetime import datetime
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from misc import saveToTempFile

from gnss.satellite import SatelliteInView

class MiscStatsWindow(QMainWindow):
	"""Window for displaying miscellaneous statistics"""

	satelliteReceivedEvent = pyqtSignal()
	def __init__(self, palette):
		super().__init__()
		self.setWindowTitle("Misc Stats")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.latestSatellites = []
		self.latitude = 0
		self.longitude = 0
		self.date = datetime.now()
		self.altitude = 0
		self.geoidSeparation = 0
		self.horizontalDilutionOfPrecision = 0
		self.fixQuality = 0

		self.svgFont = Font("./font/01347-80012.bin")
		svgStr, width, height = makeSvgString(self.svgFont,
			"Waiting for data...".encode('ascii'),
			scale=2, border=4, offset=0, addGrid=False, drawShadow=False, fontThickness=1.4, fontColour="#ffffff")
		svgFile = saveToTempFile(svgStr)
		self.svg = QSvgWidget(svgFile, parent=self)
		self.svg.setGeometry(0, 0, width, height)

		self.setGeometry(0, 0, 500, 500)
		self.show()

	def onNewData(self,
	       satellites: list[SatelliteInView],
				 latitude: float,
				 longitude: float,
				 date: datetime,
				 altitude: float,
				 geoidSeparation: float,
				 horizontalDilutionOfPrecision: float,
				 fixQuality: int):
		"""Update window with new data"""
		self.latestSatellites = satellites
		self.latitude = latitude
		self.longitude = longitude
		self.date = date
		self.altitude = altitude
		self.geoidSeparation = geoidSeparation
		self.horizontalDilutionOfPrecision = horizontalDilutionOfPrecision
		self.fixQuality = fixQuality

		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		strToDisplay = f"Lat: {self.latitude:.6f}\n\rLong: {self.longitude:.6f}\n\r"
		strToDisplay += f"Date: {self.date.strftime('%Y-%m-%d')}\n\r"
		strToDisplay += f"Time: {self.date.strftime('%H:%M:%S')}\n\r"
		strToDisplay += f"Altitude: {self.altitude:.1f}\n\r"
		strToDisplay += f"Geoid Separation: {self.geoidSeparation:.1f}\n\r"
		strToDisplay += f"HDOP: {self.horizontalDilutionOfPrecision:.2f} ({classifyHDOP(self.horizontalDilutionOfPrecision)})\n\r"
		strToDisplay += f"Fix Quality: {self.fixQuality} ({classifyFixQuality(self.fixQuality)})\n\r"

		svgStr, width, height = makeSvgString(self.svgFont,
			strToDisplay.encode('ascii'),
			scale=2, border=4, offset=0, addGrid=False, drawShadow=False, fontThickness=2, fontColour="#ffffff")
		svgFile = saveToTempFile(svgStr)
		self.svg.load(svgFile)
		self.svg.setGeometry(0, 0, width, height)

def classifyHDOP(hdop: float) -> str:
	if hdop < 1:
		return "Ideal"
	if hdop < 2:
		return "Excellent"
	if hdop < 5:
		return "Good"
	if hdop < 10:
		return "Moderate"
	if hdop < 20:
		return "Fair"
	return "Poor"

def classifyFixQuality(fixQuality: int) -> str:
	if fixQuality == 0:
		return "Invalid"
	if fixQuality == 1:
		return "GPS"
	if fixQuality == 2:
		return "DGPS"
	print(f"Unknown fix quality: {fixQuality}")
	return "Unknown"
