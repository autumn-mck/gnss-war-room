import csv
import itertools
import math

# see https://download.geonames.org/export/dump/ (readme at bottom)

def getCities() -> list[list[str]]:
	"""Get a filtered list of cities to display on the map"""
	cities: list[list[str]] = []

	citiesByCountry = readCityInfo()
	countriesInfo = readCountryInfo()

	for country in citiesByCountry:
		citiesInCountry = citiesByCountry[country]
		countryInfo = countriesInfo[country]

		citiesInCountry = filterToMinPop(citiesInCountry, 100000)
		citiesInCountry = sortCitiesByPop(citiesInCountry)
		citiesInCountry = filterToMaxNumCities(citiesInCountry, countryInfo)

		# does this one do much at this point?
		citiesInCountry = filterToPopPercent(citiesInCountry, countryInfo, 0.2, 3)

		cities += citiesInCountry

	return cities

def filterToMinPop(citiesInCountry: list[list[str]], minPop: int) -> list[list[str]]:
	return [city for city in citiesInCountry if int(city[14]) > minPop]

def filterToPopPercent(citiesInCountry: list[list[str]],
											 countryInfo: list[str],
											 percent: float,
											 minCities: int
											 ) -> list[list[str]]:
	""":param citiesInCountry: sorted list of cities in a country"""
	countryPop = float(countryInfo[7])
	addedPop = 0
	addedCount = 0

	filteredCities = []
	for city in citiesInCountry:
		filteredCities.append(city)

		addedPop += int(city[14])
		addedCount += 1

		if addedPop > countryPop * percent and addedCount > minCities:
			break

	return filteredCities

def filterToMaxNumCities(citiesInCountry: list[list[str]], countryInfo: list[str]):
	""":param citiesInCountry: sorted list of cities in a country"""
	return citiesInCountry[:calcMaxNumCitiesToInclude(countryInfo)]

def sortCitiesByPop(citiesInCountry: list[list[str]]):
	return sorted(citiesInCountry, key=lambda x: int(x[14]), reverse=True)

def calcMaxNumCitiesToInclude(countryInfo: list[str]) -> int:
	"""Calculate the maximum number of cities to include in a country, based on both its population and area"""
	extraCityPerMillion = 0.05
	extraCityPerThousandKm2 = 0.05

	area = float(countryInfo[6]) / 1000
	popMillions = int(countryInfo[7]) / 1000000
	return int(popMillions * extraCityPerMillion + area * extraCityPerThousandKm2)

def readCityInfo() -> dict[str, list[list[str]]]:
	"""Read the city info from the file and group it by country"""
	rawCityInfo = readTSV("./map/cities15000.txt")
	cityInfo = {
		country: list(cities)
		for country, cities in itertools.groupby(rawCityInfo, key=lambda x: x[8])
	}
	return cityInfo

def findNearestCity(lat: float, long: float) -> list[str]:
	"""Find the nearest city to a given lat/long"""
	cities = readTSV("./map/cities15000.txt")

	nearestCity = None
	nearestDist = math.inf
	for city in cities:
		cityLat = float(city[4])
		cityLong = float(city[5])
		dist = distBetweenPoints(lat, long, cityLat, cityLong)
		if dist < nearestDist:
			nearestDist = dist
			nearestCity = city

	if nearestCity is None:
		# should never happen, something is badly wrong
		raise ValueError("No nearest city found")

	return nearestCity

def distBetweenPoints(lat1: float, long1: float, lat2: float, long2: float) -> float:
	return (lat2 - lat1)**2 + (long2 - long1)**2

def readCountryInfo() -> dict[str, list[str]]:
	rawCountryInfo = readTSV("./map/countryInfo.txt")
	countryInfo = {
		row[0]: row for row in rawCountryInfo # key is the country code
	}
	return countryInfo

def readTSV(filename: str) -> list[list[str]]:
	with open(filename, "r", encoding="utf8") as f:
		rd = csv.reader(f, delimiter="\t")
		return list(rd)
