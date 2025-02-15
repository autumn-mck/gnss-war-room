import math
from palettes.palette import Palette
from gnss.satellite import SatelliteInView, colourForNetwork


def azimuthToPolarCoords(azimuth: float, elevation: float, scale: float):
	radius = math.cos(math.radians(elevation)) * scale / 2
	angle = math.radians(azimuth)
	x = radius * math.sin(angle) + scale / 2
	y = scale / 2 - radius * math.cos(angle)
	return (x, y)


def addSatellitesToPolarGrid(
	svgData: str, palette: Palette, satellites: list[SatelliteInView]
) -> str:
	"""Add satellite positions to the SVG"""
	scale = 94
	satelliteStr: str = '<g id="Satellites">'
	for satellite in satellites:
		colour = colourForNetwork(satellite.network, palette)
		azimuth = satellite.azimuth
		elevation = satellite.elevation
		(x, y) = azimuthToPolarCoords(azimuth, elevation, scale)
		satelliteStr += f'<circle cx="{x}" cy="{y}" r="2" fill="{colour}" />'
	satelliteStr += "</g></svg>"

	svgData = svgData.replace("</svg>", satelliteStr)

	return svgData
