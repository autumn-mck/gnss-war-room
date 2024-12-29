from gnss.satellite import SatelliteInView, colourForNetwork, getSatelliteLatLong
from palettes.palette import Palette
from config import MapConfig
from map.gallStereographic import latLongToGallStereographic
from map.generate import getMapSize

def addSatellites(
			     mapSvg: str,
					 satellites: list[SatelliteInView],
					 options: MapConfig,
					 palette: Palette,
					 measuredLatitude: float,
					 measuredLongitude: float
					 ) -> str:
	"""Insert satellite positions into the SVG"""
	mapWidth, mapHeight = getMapSize()

	satelliteStr = '<g id="Satellites">\n'

	for satellite in satellites:
		colour = colourForNetwork(satellite.network, palette)
		lat, long = getSatelliteLatLong(satellite)
		lat += measuredLatitude
		long += measuredLongitude

		[x, y] = latLongToGallStereographic(lat, long, mapWidth)
		x += mapWidth / 2
		y += mapHeight / 2
		radius = 30 / options.scaleFactor
		satelliteStr += f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{colour}" />'
	satelliteStr += '</g></svg>'
	return mapSvg.replace('</svg>', satelliteStr)

def focusOnPoint(mapSvg: str, options: MapConfig, desiredWidth: float, desiredHeight: float) -> str:
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