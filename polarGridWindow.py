import math
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QResizeEvent
from palettes.palette import Palette
from mapdata.maps import saveToTempFile
from gnss.satellite import SatelliteInView, colourForNetwork

class PolarGridWindow(QMainWindow):
	"""Window for displaying the positions of satellites"""
	def __init__(self, palette: Palette):
		super().__init__()
		self.setWindowTitle("Polar Grid")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette

		with open("mapdata/polar.svg", "r", encoding="utf8") as f:
			svgData = f.read()

		initialSatellites = [] # wait for data
		svgData = prepareSvg(svgData, palette, initialSatellites)
		self.svgFile = saveToTempFile(svgData)
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, 400, 400)

		self.show()

	def resizeEvent(self, event: QResizeEvent):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()
		minSize = min(newX, newY)
		self.map.setGeometry(0, 0, minSize, minSize)

	def onSatellitesReceived(self, satellites: list[SatelliteInView]):
		"""Update the positions of satellites"""
		with open("mapdata/polar.svg", "r", encoding="utf8") as f:
			svgData = f.read()
		svgData = prepareSvg(svgData, self.customPalette, satellites)
		self.svgFile = saveToTempFile(svgData)
		self.map.load(self.svgFile)


def prepareSvg(svgData, palette, satelites: list[SatelliteInView]) -> str:
	"""Apply color palette to the SVG and add satellite positions"""
	svgData = svgData.replace('fill="#fff"', f'fill="{palette.background}"')
	svgData = svgData.replace('stroke="#aaa"', f'stroke="{palette.foreground}"')
	svgData = svgData.replace('stroke="#000"', f'stroke="{palette.foreground}" style="display:none"')

	scale = 94

	sateliteStr: str = '<g id="Satellites">'
	for satelite in satelites:
		colour = colourForNetwork(satelite.network, palette)
		azimuth = satelite.azimuth
		elevation = satelite.elevation
		(x, y) = azimuthToPolarCoords(azimuth, elevation, scale)
		sateliteStr += f'<circle cx="{x}" cy="{y}" r="2" fill="{colour}" />'
	sateliteStr += '</g></svg>'

	svgData = svgData.replace('</svg>', sateliteStr)

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
