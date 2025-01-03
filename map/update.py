from gnss.satellite import SatelliteInView, colourForNetwork, getSatelliteLatLong
from misc import Size
from palettes.palette import Palette
from config import MapConfig
from map.gallStereographic import latLongToGallStereographic
from map.generate import getMapSize


def genSatelliteMapGroup(
	options: MapConfig,
	palette: Palette,
	satellites: list[SatelliteInView],
	measuredLatitude: float,
	measuredLongitude: float,
) -> str:
	"""Generate an SVG group of satellite positions"""
	mapSize = getMapSize()

	radius = 30 / options.scaleFactor
	satelliteStr = '\t<g id="Satellites">\n'

	for satellite in satellites:
		colour = colourForNetwork(satellite.network, palette)
		(lat, long) = getSatelliteLatLong(satellite)
		lat += measuredLatitude
		long += measuredLongitude

		[x, y] = latLongToGallStereographic(lat, long, mapSize.width)
		x += mapSize.width / 2
		y += mapSize.height / 2

		satelliteStr += f'\t\t<circle cx="{x:.4f}" cy="{y:.4f}" fill="{colour}" r="{radius}" />\n'
	satelliteStr += "\t</g>"
	return satelliteStr


def focusOnPoint(
	mapSvg: str,
	options: MapConfig,
	desiredSize: Size,
	keySize: Size,
	keyXMult: float = 1,
	keyYMult: float = 1,
) -> str:
	"""Focus map on a given Lat/Long."""
	mapSize = getMapSize()

	(projectedX, projectedY) = latLongToGallStereographic(
		options.focusLat, options.focusLong, mapSize.width
	)
	projectedX += mapSize.width / 2
	projectedY += mapSize.height / 2

	newSize = calcNewDimensions(mapSize, options.scaleMethod, options.scaleFactor, desiredSize)

	newX = projectedX - newSize.width / 2
	newY = projectedY - newSize.height / 2

	if options.hideKey:
		mapSvg = mapSvg.replace('<g id="Key">', '<g id="Key" style="display:none">')

	if not options.hideKey:
		newGroupStr = genNewKeyGoup(options, newSize, keySize, keyXMult, keyYMult, newX, newY)
		mapSvg = mapSvg.replace('<g id="Key">', newGroupStr)

	return replaceViewBox(mapSvg, f"{newX} {newY} {newSize.width} {newSize.height}")


def genNewKeyGoup(
	options: MapConfig,
	newSize: Size,
	keySize: Size,
	keyXMult: float,
	keyYMult: float,
	newX: float,
	newY: float,
) -> str:
	"""Generate the new key group with the correct position and scale"""
	inverseScaleFactor = 1 / options.scaleFactor
	keyNewX = newX + (newSize.width - keySize.width * inverseScaleFactor) * keyXMult
	keyNewY = newY + (newSize.height - keySize.height * inverseScaleFactor) * keyYMult
	return f'<g id="Key" transform="translate({keyNewX} {keyNewY}) scale({inverseScaleFactor})">'


def replaceViewBox(mapSvg: str, newViewBox: str) -> str:
	viewboxLen = len('viewBox="')
	viewBoxStart = mapSvg.find('viewBox="')
	viewBoxEnd = mapSvg.find('"', viewBoxStart + viewboxLen)
	return mapSvg[: viewBoxStart + viewboxLen] + newViewBox + mapSvg[viewBoxEnd:]


def calcNewDimensions(
	mapSize: Size, scaleMethod: str, scaleFactor: float, desiredSize: Size
) -> Size:
	"""Calculate new dimensions for the map based on the given options."""

	match scaleMethod:
		case "constantScale":
			newWidth = desiredSize.width / scaleFactor * 3
			newHeight = desiredSize.height / scaleFactor * 3
		case "withWidth":
			newWidth = mapSize.width / scaleFactor
			newHeight = newWidth * desiredSize.height / desiredSize.width
		case "withHeight":
			newHeight = mapSize.height / scaleFactor
			newWidth = newHeight * desiredSize.width / desiredSize.height
		case "fit":
			if desiredSize.width / mapSize.width < desiredSize.height / mapSize.height:
				newWidth = mapSize.width / scaleFactor
				newHeight = newWidth * desiredSize.height / desiredSize.width
			else:
				newHeight = mapSize.height / scaleFactor
				newWidth = newHeight * desiredSize.width / desiredSize.height
		case _:
			raise ValueError(f"Invalid scale method: {scaleMethod}")

	return Size(newWidth, newHeight)
