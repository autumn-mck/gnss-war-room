# pylint: skip-file
from pytest import approx
from gnss.satellite import getSatelliteLatLong


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
