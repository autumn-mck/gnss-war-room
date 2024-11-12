import csv
import itertools

# see https://download.geonames.org/export/dump/ (readme at bottom)

def getCities() -> list:
	cities = []

	citiesByCountry = readCityInfo()
	countriesInfo = readCountryInfo()

	for country in citiesByCountry:
		citiesInCountry = citiesByCountry[country]
		countryInfo = countriesInfo[country]

		citiesInCountry = filterToMinPop(citiesInCountry, 100000)
		citiesInCountry = sortCitiesByPop(citiesInCountry)
		citiesInCountry = filterToMaxNumCities(citiesInCountry, countryInfo)
		citiesInCountry = filterToPopPercent(citiesInCountry, countryInfo, 0.2, 3) # does this one do much at this point?

		cities += citiesInCountry

	return cities

def filterToMinPop(citiesInCountry: list[list[str]], minPop: int) -> list[list[str]]:
	return [city for city in citiesInCountry if int(city[14]) > minPop]

def filterToPopPercent(citiesInCountry: list[list[str]], countryInfo: list[str], percent: float, minCities: int) -> list[list[str]]:
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

def calcMaxNumCitiesToInclude(countryInfo) -> int:
	# proportional to area and population
	extraCityPerMillion = 0.05
	extraCityPerThousandKm2 = 0.05

	area = float(countryInfo[6]) / 1000
	popMillions = int(countryInfo[7]) / 1000000
	return int(popMillions * extraCityPerMillion + area * extraCityPerThousandKm2)

def readCityInfo():
	rawCityInfo = readTSV("./mapdata/cities15000.txt")
	cityInfo = {
		country: list(cities)
		for country, cities in itertools.groupby(rawCityInfo, key=lambda x: x[8])
	}
	return cityInfo

def readCountryInfo():
	rawCountryInfo = readTSV("./mapdata/countryInfo.txt")
	countryInfo = {
		row[0]: row for row in rawCountryInfo
	}
	return countryInfo

def readTSV(filename: str) -> list[list[str]]:
	with open(filename, "r", encoding="utf8") as f:
		rd = csv.reader(f, delimiter="\t")
		return [row for row in rd]