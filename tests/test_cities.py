# pylint: skip-file
from map.cities import findNearestCity


def test_finds_nearest_city():
	assert findNearestCity(54.6, -6) == "Belfast"  # west of Belfast
	assert findNearestCity(54.35, 18.65) == "Gdansk"  # middle of Gdańsk, right in the old town
	assert findNearestCity(41.1, -81.5) == "Akron"  # middle of Akron, Ohio
	assert findNearestCity(-34.6, -58.38) == "Buenos Aires"  # middle of Buenos Aires, Argentina
	assert findNearestCity(25, 121.56) == "Taipei"  # on the edge of Taipei, Taiwan
	assert findNearestCity(69.5, 19) == "Tromso"  # down a bit from Tromsø, Norway
	assert findNearestCity(30.05, 31.24) == "Cairo"  # middle-ish of Cairo, Egypt
