import math
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtCore import pyqtSignal
from palettes.palette import Palette
from misc import saveToTempFile
from gnss.satellite import SatelliteInView, colourForNetwork

class PolarGridWindow(QMainWindow):
	"""Window for displaying the positions of satellites"""
	satelliteReceivedEvent = pyqtSignal()

	def __init__(self, palette: Palette):
		super().__init__()

		self.customPalette = palette
		self.latestSatellites = []

		self.svgFile = self.generateNewGrid()
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, 400, 400)

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.setWindowTitle("Polar Grid")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.show()

	def generateNewGrid(self):
		with open("map/polar.svg", "r", encoding="utf8") as f:
			svgData = f.read()
		svgData = prepareSvg(svgData, self.customPalette, [])
		return saveToTempFile(svgData)

	def updateGrid(self):
		with open("map/polar.svg", "r", encoding="utf8") as f:
			svgData = f.read()
		svgData = prepareSvg(svgData, self.customPalette, self.latestSatellites)
		return saveToTempFile(svgData)

	def resizeEvent(self, event: QResizeEvent):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()
		minSize = min(newX, newY)
		self.map.setGeometry(0, 0, minSize, minSize)

	def onNewData(self, satellites: list[SatelliteInView]):
		self.latestSatellites = satellites
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		self.svgFile = self.updateGrid()
		self.map.load(self.svgFile)

def prepareSvg(svgData: str, palette: Palette, satellites: list[SatelliteInView]) -> str:
	"""Apply color palette to the SVG and add satellite positions"""
	svgData = svgData.replace('fill="#fff"', f'fill="{palette.background}"')
	svgData = svgData.replace('stroke="#aaa"', f'stroke="{palette.polarGrid}"')
	svgData = svgData.replace('stroke="#000"', f'stroke="{palette.polarGrid}" style="display:none"')

	scale = 94
	satelliteStr: str = '<g id="Satellites">'
	for satellite in satellites:
		colour = colourForNetwork(satellite.network, palette)
		azimuth = satellite.azimuth
		elevation = satellite.elevation
		(x, y) = azimuthToPolarCoords(azimuth, elevation, scale)
		satelliteStr += f'<circle cx="{x}" cy="{y}" r="2" fill="{colour}" />'
	satelliteStr += '</g></svg>'

	svgData = svgData.replace('</svg>', satelliteStr)

	return svgData

def azimuthToPolarCoords(azimuth: float, elevation: float, scale: float):
	radius = math.cos(math.radians(elevation)) * scale / 2
	angle = math.radians(azimuth)
	x = radius * math.sin(angle) + scale / 2
	y = scale / 2 - radius * math.cos(angle)
	return (x, y)

def readBaseSvg() -> str:
	with open("mapdata/polar.svg", "r", encoding="utf8") as f:
		return f.read()
