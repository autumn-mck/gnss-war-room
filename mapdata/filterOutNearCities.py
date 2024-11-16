def filterOutCitiesNearOtherCities(citiesInCountry: list[list[str]]) -> list[list[str]]:
	"""Filter out cities that are geographically close to other cities"""
	cities = []
	for city in citiesInCountry:
		if all(not areCitiesNearby(city, city2) for city2 in cities):
			cities.append(city)
	return cities

def areCitiesNearby(city1: list[str], city2: list[str]) -> bool:
	"""Check if two cities are geographically close"""
	cityLat = float(city1[4])
	cityLong = float(city1[5])

	cityLat2 = float(city2[4])
	cityLong2 = float(city2[5])
	return (cityLat - cityLat2)**2 + (cityLong - cityLong2)**2 < 20
