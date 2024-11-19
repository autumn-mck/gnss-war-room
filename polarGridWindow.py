import math
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QResizeEvent
from palettes.palette import Palette
from mapdata.maps import saveToTempFile
from nmea import getSatelitesGroupedByPrn

class PolarGridWindow(QMainWindow):
	"""Window for displaying the positions of satellites"""
	def __init__(self, palette: Palette):
		super().__init__()
		self.setWindowTitle("Polar Grid")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

		with open("mapdata/polar.svg", "r", encoding="utf8") as f:
			svgData = f.read()

		svgData = prepareSvg(svgData, palette)
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


def prepareSvg(svgData, palette) -> str:
	"""Apply color palette to the SVG and add satellite positions"""
	svgData = svgData.replace('fill="#fff"', f'fill="{palette.background}"')
	svgData = svgData.replace('stroke="#aaa"', f'stroke="{palette.foreground}"')
	svgData = svgData.replace('stroke="#000"', f'stroke="{palette.foreground}" style="display:none"')

	scale = 94

	colours = [
		"#ff0000",
		"#ff00ff",
		"#00ff00",
		"#0000ff",
		"#ffff00",
		"#00ffff",
		"#ffffff"
	]

	satelites = getSatelitesGroupedByPrn()
	sateliteStr: str = '<g id="Satellites">'
	count = 0
	for _, satelites in satelites.items():
		for satelite in satelites:
			azimuth = satelite.azimuth
			elevation = satelite.elevation
			(x, y) = azimuthToPolarCoords(azimuth, elevation, scale)
			sateliteStr += f'<circle cx="{x}" cy="{y}" r="2" fill="{colours[count]}" />'
		count += 1
		if count % len(colours) == 0:
			count = 0
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
