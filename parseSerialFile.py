from datetime import datetime
from time import sleep

def parseThroughLinesOnTime(lines: list[str]):
	"""Parse a list of lines, waiting for the timestamp to pass"""
	lastTimestamp = None

	for line in lines:
		data = line.split('\t')
		timestamp = data[0]
		nmeaMessage = data[1]
		parsedTimestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

		if lastTimestamp is not None:
			delta = parsedTimestamp - lastTimestamp
			sleep(delta.total_seconds())
		print(nmeaMessage.strip())
		lastTimestamp = parsedTimestamp

def main():
	with open('test.nmea', 'r', encoding='utf-8') as f:
		lines = f.readlines()
	parseThroughLinesOnTime(lines)

if __name__ == "__main__":
	main()
