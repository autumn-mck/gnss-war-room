import csv
import itertools
import math
import os

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


def filterToPopPercent(
	citiesInCountry: list[list[str]], countryInfo: list[str], percent: float, minCities: int
) -> list[list[str]]:
	""":param citiesInCountry: sorted list of cities in a country"""
	countryPop = float(countryInfo[7])
	addedPop = 0

	filteredCities = []
	for addedCount, city in enumerate(citiesInCountry, 1):
		filteredCities.append(city)

		addedPop += int(city[14])

		if addedPop > countryPop * percent and addedCount > minCities:
			break

	return filteredCities


def filterToMaxNumCities(citiesInCountry: list[list[str]], countryInfo: list[str]):
	""":param citiesInCountry: sorted list of cities in a country"""
	return citiesInCountry[: calcMaxNumCitiesToInclude(countryInfo)]


def sortCitiesByPop(citiesInCountry: list[list[str]]):
	return sorted(citiesInCountry, key=lambda x: int(x[14]), reverse=True)


def calcMaxNumCitiesToInclude(countryInfo: list[str]) -> int:
	"""Calculate the maximum number of cities to include in a country, based on both its population
	and area
	"""
	extraCityPerMillion = 0.05
	extraCityPerThousandKm2 = 0.05

	area = float(countryInfo[6]) / 1000
	popMillions = int(countryInfo[7]) / 1000000
	return int(popMillions * extraCityPerMillion + area * extraCityPerThousandKm2)


def readCityInfo() -> dict[str, list[list[str]]]:
	"""Read the city info from the file and group it by country"""
	rawCityInfo = readTSV("./views/map/cities15000.txt")
	return {
		country: list(cities)
		for country, cities in itertools.groupby(rawCityInfo, key=lambda x: x[8])
	}


def findNearestCity(lat: float, long: float, file: str = "./views/map/cities15000.txt"):
	"""Find the nearest city to a given lat/long"""
	cities = readTSV(file)

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
		return []

	return nearestCity


def findNearestCityWithCache(lat: float, long: float):
	"""Find the nearest city to the given lat/long, using the cache file if possible"""
	nearestCity = findNearestCity(lat, long, "./views/map/citiesCache.txt")

	if len(nearestCity) > 0:
		margin = 0.1
		if abs(lat - float(nearestCity[4])) < margin and abs(long - float(nearestCity[5])) < margin:
			return nearestCity[2]

	nearestCity = findNearestCity(lat, long, "./views/map/cities15000.txt")
	appendToCache(nearestCity)
	return nearestCity[2]


def appendToCache(city: list[str]):
	"""Append a city to the cache file"""
	strToAppend = ""
	for index, string in enumerate(city):
		strToAppend += string
		if index != len(city) - 1:
			strToAppend += "\t"
	with open("./views/map/citiesCache.txt", "a", encoding="utf-8") as file:
		file.write(strToAppend + "\n")


def distBetweenPoints(lat1: float, long1: float, lat2: float, long2: float) -> float:
	return (lat2 - lat1) ** 2 + (long2 - long1) ** 2


def readCountryInfo() -> dict[str, list[str]]:
	rawCountryInfo = readTSV("./views/map/countryInfo.txt")
	return {row[0]: row for row in rawCountryInfo}  # key is the country code


def readTSV(filename: str) -> list[list[str]]:
	"""Read a TSV file"""
	if not os.path.exists(filename):
		return []

	with open(filename, "r", encoding="utf8") as f:
		rd = csv.reader(f, delimiter="\t")
		return list(rd)
