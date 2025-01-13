from datetime import datetime
import math
from dataclasses import dataclass, field
from typing import Any

from palettes.palette import Palette, loadPalette


@dataclass
class SatelliteInView:
	"""Data about a GNSS satellite"""

	prnNumber: int = 0
	network: str = "??"
	elevation: float = 0
	azimuth: float = 0
	previousPositions: list[tuple[float, float]] = field(default_factory=list)
	snr: float = 0
	lastSeen: datetime = datetime.fromtimestamp(0)

	def toJSON(self, measuredFromLat: float, measuredFromLong: float) -> dict[str, Any]:
		lat, long = getSatelliteLatLong(
			self.azimuth, self.elevation, self.network, measuredFromLat, measuredFromLong
		)

		return {
			"prnNumber": self.prnNumber,
			"network": self.network,
			"elevation": self.elevation,
			"azimuth": self.azimuth,
			"snr": self.snr,
			"lastSeen": self.lastSeen.isoformat(),
			"lat": lat,
			"long": long,
			"colour": colourForNetwork(self.network),
			"altitude": orbitHeightForNetwork(self.network),
		}


def groupSatellitesByPrn(satellites: list[SatelliteInView]) -> dict[int, list[SatelliteInView]]:
	"""Group satellites by PRN number"""
	satellitesByPrn = {}
	for satellite in satellites:
		if satellite.prnNumber not in satellitesByPrn:
			satellitesByPrn[satellite.prnNumber] = []
		satellitesByPrn[satellite.prnNumber].append(satellite)
	return satellitesByPrn


def colourForNetwork(network: str, palette: Palette = loadPalette()) -> str:
	networkName = networkCodeToName(network)
	if networkName in palette.satelliteNetworks:
		return palette.satelliteNetworks[networkName]
	return palette.satelliteNetworks["Unknown"]


def networkCodeToName(networkCode: str) -> str:
	match networkCode:
		case "GA":
			return "Galileo"
		case "GP":
			return "GPS"
		case "GL":
			return "GLONASS"
		case "BD" | "GB":
			return "BeiDou"
		case _:
			return "Unknown"


def orbitHeightForNetwork(network: str) -> float:
	match network:
		case "GA":  # Galileo
			return 23.222
		case "GP":  # GPS
			return 20.18
		case "GL":  # GLONASS
			return 19.13
		case (
			"BD"
			| "GB"
		):  # BeiDou (todo: there appears to be satellites at a few different orbit heights)
			return 21.528
		case _:  # something else I need to add
			print(network)
			return 21.0  # in the middle-ish


def azimuthToWorldXyz(
	azimuth: float, elevation: float, satelliteNetwork: str
) -> tuple[float, float, float]:
	"""Projecting from the azimuth and elevation to the world xyz coordinates
	:param azimuth: azimuth in radians
	:param elevation: elevation in radians
	"""
	# https://www.desmos.com/3d/jxqcoesfg3 for visualisation of 3d,
	# https://www.desmos.com/calculator/oskkcd5rdb for 2d

	orbit = orbitHeightForNetwork(satelliteNetwork)
	ground = 6.37

	x1, x2 = calcX(elevation, orbit, ground)
	x1 *= math.cos(math.radians(azimuth))
	x2 *= math.cos(math.radians(azimuth))

	y1, y2 = calcY(elevation, orbit, ground)

	z1 = x1 * math.tan(math.radians(azimuth))
	z2 = x2 * math.tan(math.radians(azimuth))

	# divide by orbit
	x1 /= orbit
	y1 /= orbit
	z1 /= orbit

	x2 /= orbit
	y2 /= orbit
	z2 /= orbit

	return (x1, y2, z1)


def calcY(elevation: float, orbit: float, ground: float) -> tuple[float, float]:
	"""Calculate possible global Y coordinates of a satellite"""
	if elevation == 0:
		return (ground, ground)

	yConst = 1 / (math.tan(math.radians(elevation))) ** 2
	ay = -1 - yConst
	by = 2 * ground * yConst
	cy = orbit**2 - ground**2 * yConst

	y1, y2 = quadraticFormula(ay, by, cy)
	return y1, y2


def calcX(elevation: float, orbit: float, ground: float) -> tuple[float, float]:
	"""Calculate possible global X coordinates of a satellite"""
	if elevation == 90:
		return 0, 0

	ax = 1 + math.tan(math.radians(elevation)) ** 2
	bx = 2 * ground * math.tan(math.radians(elevation))
	cx = ground**2 - orbit**2

	x1, x2 = quadraticFormula(ax, bx, cx)
	return x1, x2


def quadraticFormula(a: float, b: float, c: float) -> tuple[float, float]:
	discriminant = b**2 - 4 * a * c
	root1 = (-b + math.sqrt(discriminant)) / (2 * a)
	root2 = (-b - math.sqrt(discriminant)) / (2 * a)
	return (root1, root2)


def xyzToLatLong(x: float, y: float, z: float) -> tuple[float, float]:
	"""Projecting from the xyz coordinates to the lat long coordinates. XYZ should be in the range [-1, 1]"""
	lat = math.degrees(math.asin(x))
	long = math.degrees(math.atan2(z, y))
	return (lat, long)


def rotateXyzByLatitude(x: float, y: float, z: float, lat: float) -> tuple[float, float, float]:
	"""Rotate the xyz coordinates by the given longitude"""
	rotationAngle = math.radians(-lat)
	x2 = x * math.cos(rotationAngle) - y * math.sin(rotationAngle)
	y2 = x * math.sin(rotationAngle) + y * math.cos(rotationAngle)
	return (x2, y2, z)


def getSatelliteLatLong(
	azimuth: float,
	elevation: float,
	satelliteNetwork: str,
	measuredFromLat: float,
	measuredFromLong: float,
) -> tuple[float, float]:
	"""Get the lat long coordinates of a satellite"""
	x, y, z = azimuthToWorldXyz(azimuth, elevation, satelliteNetwork)
	x, y, z = rotateXyzByLatitude(x, y, z, measuredFromLat)
	lat, long = xyzToLatLong(x, y, z)
	long += measuredFromLong
	return (lat, long)


def isSameSatellite(satellite1: SatelliteInView, satellite2: SatelliteInView) -> bool:
	return satellite1.prnNumber == satellite2.prnNumber and satellite1.network == satellite2.network
