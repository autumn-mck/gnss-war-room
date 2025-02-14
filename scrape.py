import urllib.request
import gzip
from datetime import datetime, timedelta
import h3


def main():
	"""Fetch the latest gpsJam data and print the data for Belfast-ish"""
	date = datetime.now()
	csv = tryLoadCachedGpsJam(date)
	h3dict = gpsCsvToDict(csv)

	resolution = 4
	lat, long = 54.6, -6.0
	hexagon = h3.latlng_to_cell(lat, long, resolution)
	print(h3dict[hexagon])


def scrapeFile(url):
	print(f"Fetching {url}")
	with urllib.request.urlopen(url) as gzippedFile:
		file = gzip.decompress(gzippedFile.read()).decode("utf-8")
		return file


def fetchAndSaveLatestData(beforeDate: datetime):
	"""Fetch the latest gpsJam data for the given date and save it to the cache file"""
	url = f"https://gpsjam.org/data/{beforeDate.strftime('%Y-%m-%d')}-h3_4.csv"
	try:
		file = scrapeFile(url)
		with open("map/gpsJamCache.csv", "w", encoding="utf-8") as f:
			f.write(f"{beforeDate.strftime('%Y-%m-%d')}\n")
			f.write(file)
		return file
	except urllib.request.HTTPError:
		beforeDate = beforeDate - timedelta(days=1)  # try day before
		return fetchAndSaveLatestData(beforeDate)


def gpsCsvToDict(csv: str) -> dict[str, tuple[int, int]]:
	"""Convert the given gpsJam CSV to a dict of h3 hexes to (lat, long) tuples"""
	h3Dict = {}
	for line in csv.split("\n"):
		if line.startswith("hex"):
			continue
		if line == "":
			continue
		line = line.split(",")
		good = int(line[1])
		bad = int(line[2])
		h3Dict[line[0]] = (good, bad)
	return h3Dict


def tryLoadCachedGpsJam(date: datetime):
	"""Try to load the cached gpsJam data for the given date, if it doesn't exist, fetch it"""
	try:
		with open("map/gpsJamCache.csv", "r", encoding="utf-8") as f:
			cacheDate = f.readline()
			if cacheDate.strip() == date.strftime("%Y-%m-%d"):
				return f.read()
			return fetchAndSaveLatestData(date)
	except FileNotFoundError:
		return fetchAndSaveLatestData(date)


if __name__ == "__main__":
	main()
