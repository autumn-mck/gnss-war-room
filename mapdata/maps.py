import math
import tempfile
from dataclasses import dataclass
from dataclass_wizard import JSONWizard
from palettes.palette import Palette
from mapdata.cities import getCities
from gnss.satellite import SatelliteInView, colourForNetwork, getSatelliteLatLong

@dataclass
class MapConfig(JSONWizard):
	"""Configuration for the map."""
	scaleFactor: float
	scaleMethod: str

	focusLat: float
	focusLong: float

	hideCities: bool
	hideAdmin0Borders: bool
	hideAdmin1Borders: bool
	hideRivers: bool
	hideLakes: bool

	class _(JSONWizard.Meta):
		tag = "worldMap"

@dataclass
class PolalGridConfig(JSONWizard):
	class _(JSONWizard.Meta):
		tag = "satellitePolarGrid"

def readBaseSvg() -> str:
	"""Read the base SVG map file."""
	with open("mapdata/1981.svg", "r", encoding="utf8") as f:
		return f.read()

def prepareSvg(mapSvg: str, palette: Palette, options: MapConfig, currentSatellites: list[SatelliteInView]) -> str:
	"""Apply color palette and other options to the SVG map."""
	svgOrigWidth = 3213.05005
	svgOrigHeight = 2468.23999

	# cities
	if not options.hideCities:
		cities = getCities()
		cityDataStr = '<g id="Cities">'
		for city in cities:
			cityLat = float(city[4])
			cityLong = float(city[5])
			[cityX, cityY] = latLongToGallStereographic(cityLat, cityLong, svgOrigWidth)
			cityX += svgOrigWidth / 2
			cityY += svgOrigHeight / 2

			radius = 5 / options.scaleFactor
			cityDataStr += f'<circle cx="{cityX}" cy="{cityY}" r="{radius}" fill="{palette.cities}" />'

		cityDataStr += '</g></svg>'
		mapSvg = mapSvg.replace('</svg>', cityDataStr)

	# satellites
	mapSvg = insertSatellitePositions(mapSvg, svgOrigWidth, svgOrigHeight, currentSatellites, options, palette)

	# continent border width
	continentBorderWidth = 6 / options.scaleFactor
	admin0BorderWidth = 2 / options.scaleFactor

	# waterbodies
	mapSvg = mapSvg.replace('.st0{fill:#50C8F4;', f'.st0{{fill:{palette.water};')
	mapSvg = mapSvg.replace('.st3{fill:none;stroke:#50C8F4;', f'.st3{{fill:none;stroke:{palette.water};')

	# admin1 borders
	mapSvg = mapSvg.replace('.st1{fill:none;stroke:#808080;', f'.st1{{fill:none;stroke:{palette.admin1Border};')

	# admin0 borders
	mapSvg = mapSvg.replace('.st2{fill:none;stroke:#000000;', f'.st2{{fill:none;stroke:{palette.admin0Border};')
	mapSvg = mapSvg.replace('.st2{', f'.st2{{stroke-width:{admin0BorderWidth};')

	# continent borders
	mapSvg = mapSvg.replace('stroke-width:2;', f'stroke-width:{continentBorderWidth};')
	mapSvg = mapSvg.replace('.st4{fill:none;stroke:#000000;', f'.st4{{fill:none;stroke:{palette.continentsBorder};')

	# metadata
	mapSvg = mapSvg.replace('.st5{fill:#221F1F;', f'.st5{{fill:{palette.metadata};')
	mapSvg = mapSvg.replace('.st12{fill:none;stroke:#231F20;', f'.st12{{fill:none;stroke:{palette.metadata};')

	if options.hideAdmin0Borders:
		mapSvg = mapSvg.replace('g id="Admin_0_Polygon"', 'g id="Admin_0_Polygon" style="display:none"')
		mapSvg = mapSvg.replace('g id="Admin_x5F_0_x5F_lines"', 'g id="Admin_x5F_0_x5F_lines" style="display:none"')

	if options.hideAdmin1Borders:
		mapSvg = mapSvg.replace('g id="Admin_1_Polygon"', 'g id="Admin_1_Polygon" style="display:none"')
		mapSvg = mapSvg.replace('g id="Admin_x5F_1_x5F_lines"', 'g id="Admin_x5F_1_x5F_lines" style="display:none"')

	if options.hideRivers:
		mapSvg = mapSvg.replace('g id="Rivers"', 'g id="Rivers" style="display:none"')

	if options.hideLakes:
		mapSvg = mapSvg.replace('g id="Waterbodies"', 'g id="Waterbodies" style="display:none"')

	# hide metadata
	mapSvg = mapSvg.replace('g id="MetaData"', 'g id="MetaData" style="display:none"')
	return mapSvg

def insertSatellitePositions(mapSvg: str,
			     svgOrigWidth: float,
					 svgOrigHeight: float,
					 satellites: list[SatelliteInView],
					 options: MapConfig,
					 palette: Palette
					 ) -> str:
	"""Insert satellite positions into the SVG"""
	sateliteStr = '<g id="Satellites">'

	for satellite in satellites:
		colour = colourForNetwork(satellite.network, palette)
		lat, long = getSatelliteLatLong(satellite)
		# hardcoded measure position for now
		lat += 54.5
		long += -5.9

		[x, y] = latLongToGallStereographic(lat, long, svgOrigWidth)
		x += svgOrigWidth / 2
		y += svgOrigHeight / 2
		radius = 30 / options.scaleFactor
		sateliteStr += f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{colour}" />'
	sateliteStr += '</g></svg>'
	return mapSvg.replace('</svg>', sateliteStr)

def saveToTempFile(string: str) -> str:
	"""Save a string to a temporary file and return its file path."""
	with tempfile.NamedTemporaryFile(delete=False) as temp:
		with open(temp.name, "w", encoding="utf8") as f:
			f.write(string)
	return temp.name

def focusOnPoint(mapSvg: str, options: MapConfig, desiredWidth: float, desiredHeight: float) -> str:
	"""Focus map on a given Lat/Long."""
	svgOrigWidth = 3213.05005
	svgOrigHeight = 2468.23999

	[projectedX, projectedY] = latLongToGallStereographic(options.focusLat, options.focusLong, svgOrigWidth)
	projectedX += svgOrigWidth / 2
	projectedY += svgOrigHeight / 2

	[newWidth, newHeight] = calcNewDimensions(svgOrigWidth, svgOrigHeight,
																					 options.scaleMethod, options.scaleFactor,
																					 desiredWidth, desiredHeight)

	newX = projectedX - newWidth / 2
	newY = projectedY - newHeight / 2

	viewboxLen = len('viewBox="')
	# find location of original viewbox
	viewBoxStart = mapSvg.find('viewBox="')
	viewBoxEnd = mapSvg.find('"', viewBoxStart + viewboxLen)

	return mapSvg[:viewBoxStart + viewboxLen] + f"{newX} {newY} {newWidth} {newHeight}" + mapSvg[viewBoxEnd:]

def calcNewDimensions(svgOrigWidth: float,
											svgOrigHeight: float,
											scaleMethod: str,
											scaleFactor: float,
											desiredWidth: float,
											desiredHeight: float
											) -> tuple[float, float]:
	"""Calculate new dimensions for the map based on the given options."""

	match scaleMethod:
		case "constantScale":
			newWidth = desiredWidth / scaleFactor * 3
			newHeight = desiredHeight / scaleFactor * 3
		case "withWidth":
			newWidth = svgOrigWidth / scaleFactor
			newHeight = newWidth * desiredHeight / desiredWidth
		case "withHeight":
			newHeight = svgOrigHeight / scaleFactor
			newWidth = newHeight * desiredWidth / desiredHeight
		case "fit":
			if desiredWidth / svgOrigWidth < desiredHeight / svgOrigHeight:
				newWidth = svgOrigWidth / scaleFactor
				newHeight = newWidth * desiredHeight / desiredWidth
			else:
				newHeight = svgOrigHeight / scaleFactor
				newWidth = newHeight * desiredWidth / desiredHeight
		case _:
			raise ValueError(f"Invalid scale method: {scaleMethod}")

	return (newWidth, newHeight)

def latLongToGallStereographic(lat: float, long: float, mapWidth: float) -> tuple[float, float]:
	"""Convert latitude and longitude to Gall Stereographic coordinates."""
	longOffset = -10
	long += longOffset

	# "bounce" off the top when wrapping over the poles
	if lat > 90:
		lat = 180 - lat
		long += 180
	elif lat < -90:
		lat = -180 - lat
		long += 180

	# wrap around the world as the map is not centered at 0
	if long < -180 - longOffset:
		long += 360
	elif long > 180 - longOffset:
		long -= 360

	radius = mapWidth / (2 * math.pi)
	latRad = math.radians(lat)
	longRad = math.radians(long)

	x = radius * longRad # the formula should divide by sqrt(2) here but for some reason that gives the wrong result
	y = -radius * (math.sqrt(2) + 1) * math.tan(latRad / 2)

	return (x, y)
