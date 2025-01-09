# pylint: skip-file
from map.cities import findNearestCityWithCache


def test_finds_nearest_city():
	assert findNearestCityWithCache(54.6, -6) == "Belfast"  # west of Belfast
	assert (
		findNearestCityWithCache(54.35, 18.65) == "Gdansk"
	)  # middle of Gdańsk, right in the old town
	assert findNearestCityWithCache(41.1, -81.5) == "Akron"  # middle of Akron, Ohio
	assert (
		findNearestCityWithCache(-34.6, -58.38) == "Buenos Aires"
	)  # middle of Buenos Aires, Argentina
	assert findNearestCityWithCache(25, 121.56) == "Taipei"  # on the edge of Taipei, Taiwan
	assert findNearestCityWithCache(69.5, 19) == "Tromso"  # down a bit from Tromsø, Norway
	assert findNearestCityWithCache(30.05, 31.24) == "Cairo"  # middle-ish of Cairo, Egypt
