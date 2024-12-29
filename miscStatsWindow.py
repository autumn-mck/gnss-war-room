from datetime import datetime
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from map.cities import findNearestCity
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

		self.satelliteReceivedEvent.connect(self.updateWithNewData)

		self.latestSatellites = []
		self.latitude = 0
		self.longitude = 0
		self.date = datetime.now()
		self.altitude = 0
		self.geoidSeparation = 0
		self.hdop = 0
		self.fixQuality = 0

		self.svgFont = Font()
		svgStr, width, height = makeSvgString(self.svgFont,
			"Waiting for data...".encode('ascii'),
			fontThickness=2, fontColour=palette.foreground)
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
		self.hdop = horizontalDilutionOfPrecision
		self.fixQuality = fixQuality

		self.satelliteReceivedEvent.emit()

	def updateWithNewData(self):
		"""Update the misc stats window with new data"""
		nearestCity = findNearestCity(self.latitude, self.longitude)
		cityName = nearestCity[1]

		strToDisplay = f"Lat: {self.latitude:.6f}\n\rLong: {self.longitude:.6f}\n\r"
		strToDisplay += f"Date: {self.date.strftime('%Y-%m-%d')}\n\r"
		strToDisplay += f"Time: {self.date.strftime('%H:%M:%S')}\n\r"
		strToDisplay += f"City: {cityName}\n\r"
		strToDisplay += f"Altitude: {self.altitude:.1f}\n\r"
		strToDisplay += f"Geoid Separation: {self.geoidSeparation:.1f}\n\r"
		strToDisplay += f"HDOP: {self.hdop:.2f} ({classifyDOP(self.hdop)})\n\r"
		strToDisplay += f"Fix Quality: {self.fixQuality} ({classifyFixQuality(self.fixQuality)})\n\r"

		svgStr, width, height = makeSvgString(self.svgFont,
			strToDisplay.encode('ascii'),
			fontThickness=2,
			fontColour=self.customPalette.foreground)
		svgFile = saveToTempFile(svgStr)

		width /= 2
		height /= 2
		self.svg.load(svgFile)
		self.svg.setGeometry(0, 0, int(width), int(height))

def classifyDOP(dop: float) -> str:
	"""Classify the dilution of precision"""
	if dop < 1:
		return "Ideal"
	if dop < 2:
		return "Excellent"
	if dop < 5:
		return "Good"
	if dop < 10:
		return "Moderate"
	if dop < 20:
		return "Fair"
	return "Poor"

def classifyFixQuality(fixQuality: int) -> str:
	"""Classify the GGA fix quality"""
	if fixQuality == 0:
		return "Invalid"
	if fixQuality == 1:
		return "GPS"
	if fixQuality == 2:
		return "DGPS"
	print(f"Unknown fix quality: {fixQuality}")
	return "Unknown"
