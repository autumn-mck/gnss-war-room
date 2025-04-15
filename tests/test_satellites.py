# pylint: skip-file
import math

from pytest import approx

from gnss.satellite import getSatelliteLatLong, orbitHeightForNetwork


def easaSatelliteLatLong(lat: float, long: float, elevation: float, azimuth: float, network: str):
	"""Alternate method for getting satellite lat/long using method from EASA paper
	https://www.easa.europa.eu/sites/default/files/dfu/ETSO.Dev_.C145_5_v11.pdf
	Modified from the following StackExchange answer to remove numpy as a dependency:
	https://space.stackexchange.com/a/64929/67281"""
	earthRadius = 6.37

	latRad = math.radians(lat)
	longRad = math.radians(long)

	elevationRad = math.radians(elevation)
	azimuthRad = math.radians(azimuth)

	satAltitude = orbitHeightForNetwork(network)
	psiAlt = (
		math.pi / 2 - elevationRad - math.asin(earthRadius / satAltitude * math.cos(elevationRad))
	)

	sspLat = math.asin(
		math.sin(latRad) * math.cos(psiAlt)
		+ math.cos(latRad) * math.sin(psiAlt) * math.cos(azimuthRad)
	)

	calc = math.sin(psiAlt) * math.sin(azimuthRad) / math.cos(sspLat)

	if (lat > 70 and math.tan(psiAlt) * math.cos(azimuthRad) > math.tan(math.pi / 2 - latRad)) or (
		lat < -70
		and math.tan(psiAlt) * math.cos(azimuthRad + math.pi) > math.tan(math.pi / 2 + latRad)
	):
		sspLong = longRad + math.pi - math.asin(calc)
	else:
		sspLong = longRad + math.asin(calc)

	satLat = math.degrees(sspLat)
	satLong = math.degrees(sspLong)

	return satLat, satLong


def test_easa():
	# Note: current implementation of EASA satellite position calculations is incorrect
	# as it seems to only allow satellites on a single hemisphere of the earth.
	lat = 0
	long = 0

	for azimuth in range(0, 360, 10):
		for elevation in range(0, 90, 10):
			(satLat1, satLong1) = easaSatelliteLatLong(lat, long, elevation, azimuth, "GA")
			(satLat2, satLong2) = getSatelliteLatLong(azimuth, elevation, "GA", lat, long)
			assert satLat1 == approx(satLat2)
			assert satLong1 == approx(satLong2)


def test_satelliteDirectlyAbove():
	(lat, long) = getSatelliteLatLong(0, 90, "GA", 0, 0)
	assert lat == 0
	assert long == 0


def test_angledElevation():
	(lat, long) = getSatelliteLatLong(0, 45, "GA", 0, 0)
	assert lat == approx(33.8157)
	assert long == 0


def test_rotated90():
	(lat, long) = getSatelliteLatLong(90, 45, "GA", 0, 0)
	assert lat == approx(0)
	assert long == approx(33.8157)


def test_mixedRotation():
	(lat, long) = getSatelliteLatLong(30, 45, "GA", 0, 0)
	assert lat == approx(28.8137)
	assert long == approx(18.5167)


def test_alternateNetwork():
	(lat, long) = getSatelliteLatLong(30, 45, "GP", 0, 0)
	assert lat == approx(27.4025)
	assert long == approx(17.4157)


def test_alternateMeasurementPoint():
	(lat, long) = getSatelliteLatLong(30, 45, "GA", 45, 10)
	assert lat == approx(68.1693)
	assert long == approx(58.442)
