import gzip
import urllib.request
from datetime import datetime, timedelta


def scrapeFile(url):
	print(f"Fetching {url}")
	with urllib.request.urlopen(url) as gzippedFile:
		return gzip.decompress(gzippedFile.read()).decode("utf-8")


def fetchAndSaveLatestData(beforeDate: datetime):
	"""Fetch the latest gpsJam data for the given date and save it to the cache file"""
	url = f"https://gpsjam.org/data/{beforeDate.strftime('%Y-%m-%d')}-h3_4.csv"
	try:
		file = scrapeFile(url)
		with open("views/map/gpsJamCache.csv", "w", encoding="utf-8") as f:
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
		if line and not line.startswith("hex"):
			key, good, bad = line.split(",")[:3]
			h3Dict[key] = (int(good), int(bad))
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
