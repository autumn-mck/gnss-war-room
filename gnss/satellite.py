import math
from dataclasses import dataclass

@dataclass
class SatelliteInView:
	prnNumber: int
	network: str
	elevation: float
	azimuth: float
	snr: float

def groupSatellitesByPrn(satellites: list[SatelliteInView]) -> dict[int, list[SatelliteInView]]:
	"""Group satellites by PRN number"""
	satellitesByPrn = {}
	for satellite in satellites:
		if satellite.prnNumber not in satellitesByPrn:
			satellitesByPrn[satellite.prnNumber] = []
		satellitesByPrn[satellite.prnNumber].append(satellite)
	return satellitesByPrn

def colourForNetwork(network: str) -> str:
	match network:
		case "GA": # Galileo
			return "#ff0000"
		case "GP": # GPS
			return "#ff00ff"
		case "GL": # GLONASS
			return "#00ff00"
		case "BD" | "GB": # BeiDou
			return "#0000ff"
		case _: # something else I need to add
			print(network)
			return "#ffffff"

def azimuthToWorldXyz(azimuth: float, elevation: float) -> tuple[float, float, float]:
	"""Projecting from the azimuth and elevation to the world xyz coordinates
	:param azimuth: azimuth in radians
	:param elevation: elevation in radians
	"""
	# https://www.desmos.com/3d/jxqcoesfg3 for visualisation of 3d,
	# https://www.desmos.com/calculator/9ihgqyaqkw for 2d

	orbit = 19.13
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

	return x1, y2, z1

def calcY(elevation: float, orbit: float, ground: float) -> tuple[float, float]:
	"""Calculate possible global Y coordinates of a satellite"""
	if elevation == 0:
		return ground, ground

	yConst = 1 / (math.tan(math.radians(elevation)))**2
	ay = -1 - yConst
	by = 2 * ground * yConst
	cy = orbit**2 - ground**2 * yConst

	y1, y2 = quadraticFormula(ay, by, cy)
	return y1,y2

def calcX(elevation: float, orbit: float, ground: float) -> tuple[float, float]:
	"""Calculate possible global X coordinates of a satellite"""
	if elevation == 90:
		return 0, 0

	ax = 1 + math.tan(math.radians(elevation))**2
	bx = 2 * ground * math.tan(math.radians(elevation))
	cx = ground**2 - orbit**2

	x1, x2 = quadraticFormula(ax, bx, cx)
	return x1,x2

def quadraticFormula(a: float, b: float, c: float) -> tuple[float, float]:
	discriminant = b**2 - 4 * a * c
	root1 = (-b + math.sqrt(discriminant)) / (2 * a)
	root2 = (-b - math.sqrt(discriminant)) / (2 * a)
	return root1, root2

def xyzToLatLong(x: float, y: float, z: float) -> tuple[float, float]:
	"""Projecting from the xyz coordinates to the lat long coordinates. XYZ should be in the range [-1, 1]"""
	lat = math.degrees(math.asin(x))
	long = math.degrees(math.atan2(z, y))
	return (lat, long)

def getSatelliteLatLong(satellite: SatelliteInView) -> tuple[float, float]:
	"""Get the lat long coordinates of a satellite"""
	azimuth = satellite.azimuth
	elevation = satellite.elevation
	x, y, z = azimuthToWorldXyz(azimuth, elevation)
	lat, long = xyzToLatLong(x, y, z)
	return (lat, long)
