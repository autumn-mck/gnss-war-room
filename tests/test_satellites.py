# pylint: skip-file
from pytest import approx
from gnss.satellite import SatelliteInView, getSatelliteLatLong


def test_getSatelliteLatLong():
	"""Test that the lat/long is calculated correctly"""
	(lat, long) = getSatelliteLatLong(SatelliteInView(azimuth=0, elevation=0))
	assert lat == approx(72.3421)
	assert long == 0
