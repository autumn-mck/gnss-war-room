from gnss.satellite import SatelliteInView, colourForNetwork, getSatelliteLatLong
from palettes.palette import Palette
from config import MapConfig
from map.gallStereographic import latLongToGallStereographic
from map.generate import getMapSize

def genSatelliteMapGroup(options: MapConfig,
					palette: Palette,
					satellites: list[SatelliteInView],
					measuredLatitude: float,
					measuredLongitude: float) -> str:
	"""Generate an SVG group of satellite positions"""
	mapWidth, mapHeight = getMapSize()

	radius = 30 / options.scaleFactor
	satelliteStr = '\t<g id="Satellites">\n'

	for satellite in satellites:
		colour = colourForNetwork(satellite.network, palette)
		lat, long = getSatelliteLatLong(satellite)
		lat += measuredLatitude
		long += measuredLongitude

		[x, y] = latLongToGallStereographic(lat, long, mapWidth)
		x += mapWidth / 2
		y += mapHeight / 2

		satelliteStr += f'\t\t<circle cx="{x:.4f}" cy="{y:.4f}" fill="{colour}" r="{radius}" />\n'
	satelliteStr += '\t</g>'
	return satelliteStr

def focusOnPoint(mapSvg: str,
		 options: MapConfig,
		 desiredWidth: float, desiredHeight: float,
		 keyWidth: float, keyHeight: float,
		 keyXMult: float = 1, keyYMult: float = 1) -> str:
	"""Focus map on a given Lat/Long."""
	mapWidth, mapHeight = getMapSize()

	[projectedX, projectedY] = latLongToGallStereographic(options.focusLat, options.focusLong, mapWidth)
	projectedX += mapWidth / 2
	projectedY += mapHeight / 2

	[newWidth, newHeight] = calcNewDimensions(mapWidth, mapHeight,
																					 options.scaleMethod, options.scaleFactor,
																					 desiredWidth, desiredHeight)

	newX = projectedX - newWidth / 2
	newY = projectedY - newHeight / 2

	if options.hideKey:
		mapSvg = mapSvg.replace('<g id="Key">', '<g id="Key" style="display:none">')

	# move the key
	if not options.hideKey:
		inverseScaleFactor = 1 / options.scaleFactor
		keyNewX = newX + (newWidth - keyWidth * inverseScaleFactor) * keyXMult
		keyNewY = newY + (newHeight - keyHeight * inverseScaleFactor) * keyYMult
		newGroupStr = f'<g id="Key" transform="translate({keyNewX} {keyNewY}) scale({inverseScaleFactor})">'
		mapSvg = mapSvg.replace('<g id="Key">', newGroupStr)

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
