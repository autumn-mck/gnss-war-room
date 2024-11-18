import itertools
import math
from dataclasses import dataclass
from pynmeagps import NMEAReader, NMEAMessage

@dataclass
class SatelliteInView:
	prnNumber: int
	elevation: float
	azimuth: float
	snr: float

def parseSatelliteInMessage(parsedData: NMEAMessage) -> list[SatelliteInView]:
	"""Parse a GSV message into a list of SatelliteInView objects"""
	if parsedData.msgID != 'GSV':
		raise ValueError(f"Expected GSV message, got {parsedData.msgID}")

	return [
		SatelliteInView(
			prnNumber=getattr(parsedData, f'svid_0{satNum+1}'),
			elevation=getattr(parsedData, f'elv_0{satNum+1}'),
			azimuth=getattr(parsedData, f'az_0{satNum+1}'),
			snr=getattr(parsedData, f'cno_0{satNum+1}')
		)
		for satNum in range(3)
		if hasattr(parsedData, f'svid_0{satNum+1}')
	]

def parseNmeaFile(filename: str) -> list[NMEAMessage]:
	with open(filename, 'rb') as stream:
		nmr = NMEAReader(stream, nmeaonly=True)
		return [
			parsedData for rawData, parsedData in nmr
			if isinstance(parsedData, NMEAMessage)
		]

def selectGSV(nmeaMessages: list[NMEAMessage]) -> list[NMEAMessage]:
	return [
		parsedData for parsedData in nmeaMessages
		if parsedData.msgID == 'GSV'
	]

def groupSatellitesByPrn(satellites: list[SatelliteInView]) -> dict[int, list[SatelliteInView]]:
	"""Group satellites by PRN number"""
	satellitesByPrn = {}
	for satellite in satellites:
		if satellite.prnNumber not in satellitesByPrn:
			satellitesByPrn[satellite.prnNumber] = []
		satellitesByPrn[satellite.prnNumber].append(satellite)
	return satellitesByPrn

def getSatelitesGroupedByPrn() -> dict[int, list[SatelliteInView]]:
	"""Get satellites grouped by PRN number"""
	nmeaMessages = parseNmeaFile('test.nmea')
	gsvMessages = selectGSV(nmeaMessages)
	allSatelliteData = list(
		itertools.chain.from_iterable(
		parseSatelliteInMessage(gsvMessage)
		for gsvMessage in gsvMessages))
	satellitesByPrn = groupSatellitesByPrn(allSatelliteData)
	return satellitesByPrn

def azimuthToWorldXyz(azimuth: float, elevation: float) -> tuple[float, float, float]:
	"""Projecting from the azimuth and elevation to the world xyz coordinates
	:param azimuth: azimuth in radians
	:param elevation: elevation in radians
	"""
	# https://www.desmos.com/3d/6a3qnm1trn for visualisation of 3d,
	# https://www.desmos.com/calculator/9ihgqyaqkw for 2d

	earthRadius = 6.371 # megametres
	orbitHeight = 19.13 # megametres

	satDistance = earthRadius + orbitHeight

	y = math.sin(elevation) * orbitHeight + earthRadius
	x = math.cos(azimuth) * math.sqrt(satDistance**2 - y**2)
	z = math.sin(azimuth) * satDistance * math.cos(earthRadius / satDistance) * math.cos(elevation)

	x /= orbitHeight + earthRadius
	y /= orbitHeight + earthRadius
	z /= orbitHeight + earthRadius
	return (x, y, z)

def xyzToLatLong(x: float, y: float, z: float) -> tuple[float, float]:
	"""Projecting from the xyz coordinates to the lat long coordinates. XYZ should be in the range [-1, 1]"""
	lat = math.asin(y)
	long = math.atan2(x, z)
	return (lat, long)

def getSatelliteLatLong(satellite: SatelliteInView) -> tuple[float, float]:
	"""Get the lat long coordinates of a satellite"""
	azimuth = math.radians(satellite.azimuth)
	elevation = math.radians(satellite.elevation)
	x, y, z = azimuthToWorldXyz(azimuth, elevation)
	lat, long = xyzToLatLong(x, y, z)
	return (math.degrees(lat), math.degrees(long))
