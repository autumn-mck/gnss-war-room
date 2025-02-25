from datetime import datetime

from gnss.satellite import (
	SatelliteInView,
	colourForNetwork,
	getSatelliteLatLong,
	rotateLatLongByTime,
)
from misc.config import MapConfig
from misc.size import Size
from palettes.palette import Palette
from views.map.gallStereographic import latLongToGallStereographic
from views.map.generate import getMapSize


def genSatelliteMapGroup(
	options: MapConfig,
	palette: Palette,
	satellites: list[SatelliteInView],
	measuredLatitude: float,
	measuredLongitude: float,
	currentTime: datetime,
) -> str:
	"""Generate an SVG group of satellite positions"""
	mapSize = getMapSize()

	radius = 30 / options.scaleFactor
	satelliteStr = '\t<g id="Satellites">\n'

	if not options.hideSatelliteTrails:
		for satellite in satellites:
			satelliteStr += generateSatelliteTrails(
				satellite,
				mapSize,
				palette,
				measuredLatitude,
				measuredLongitude,
				radius,
				currentTime,
			)

	for satellite in satellites:
		satelliteStr += generateSatellitePoint(
			satellite, mapSize, palette, measuredLatitude, measuredLongitude, radius
		)
	satelliteStr += "\t</g>"
	return satelliteStr


def generateSatellitePoint(
	satellite: SatelliteInView,
	mapSize: Size,
	palette: Palette,
	measuredLatitude: float,
	measuredLongitude: float,
	radius: float,
):
	"""Generate a point for the given satellite"""
	colour = colourForNetwork(satellite.network, palette)
	(lat, long) = getSatelliteLatLong(
		satellite.azimuth,
		satellite.elevation,
		satellite.network,
		measuredLatitude,
		measuredLongitude,
	)

	[x, y] = latLongToGallStereographic(lat, long, mapSize.width)
	x += mapSize.width / 2
	y += mapSize.height / 2

	return f'\t\t<circle cx="{x:.4f}" cy="{y:.4f}" fill="{colour}" r="{radius}" />\n'


def generateSatelliteTrails(
	satellite: SatelliteInView,
	mapSize: Size,
	palette: Palette,
	measuredLatitude: float,
	measuredLongitude: float,
	baseRadius: float,
	currentTime: datetime,
):
	"""Generate a trail for the given satellite"""
	if len(satellite.previousPositions) < 1:
		return ""
	colour = colourForNetwork(satellite.network, palette)

	previousPositions = satellite.previousPositions.copy()
	previousPositions.append((satellite.lastSeen, satellite.elevation, satellite.azimuth))
	latLongs = [
		rotateLatLongByTime(
			getSatelliteLatLong(
				azimuth, elevation, satellite.network, measuredLatitude, measuredLongitude
			),
			measuredTime,
			currentTime,
		)
		for (measuredTime, elevation, azimuth) in previousPositions
	]
	mapPoints = [latLongToGallStereographic(lat, long, mapSize.width) for lat, long in latLongs]

	# split into separate polylines when distance too big (e.g. crossing antimeridian)
	mapPointsSplit: list[list[tuple[float, float]]] = []
	for index, point in enumerate(mapPoints):
		if (
			index == 0
			or abs(point[0] - mapPoints[index - 1][0]) > mapSize.width / 2
			or abs(point[1] - mapPoints[index - 1][1]) > mapSize.height / 2
		):
			mapPointsSplit.append([point])
		else:
			mapPointsSplit[-1].append(point)

	polylines = ""

	for mapPointsSet in mapPointsSplit:
		polylines += f"""\t\t<polyline
		points='{" ".join(
			f"{(x + mapSize.width / 2):.4f},{(y + mapSize.height / 2):.4f}" for x, y in mapPointsSet
		)}'
		fill='none'
		stroke='{colour}'
		stroke-width='{baseRadius / 3}'
		stroke-linecap='round'
		stroke-linejoin='round' />\n"""
	return polylines


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
			msg = f"Invalid scale method: {scaleMethod}"
			raise ValueError(msg)

	return Size(newWidth, newHeight)
