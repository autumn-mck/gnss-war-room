from datetime import datetime


def parseAndPublishLines(lines: list[str]):
	"""Parse a list of lines, waiting for the timestamp to pass"""
	lastTimestamp = None
	firstTimestamp = None

	fileToWrite = "out.txt"
	with open(fileToWrite, "w", encoding="utf-8") as f:
		for line in lines:
			timestamp, nmeaMessage = line.split("\t")
			parsedTimestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

			if firstTimestamp is None or lastTimestamp is None:
				firstTimestamp = parsedTimestamp
				lastTimestamp = parsedTimestamp

			timestampStr = f"{(parsedTimestamp - lastTimestamp).total_seconds():.6f}"

			lineOut = f"{timestampStr}\t{nmeaMessage.strip()}"
			f.write(lineOut + "\r\n")
			lastTimestamp = parsedTimestamp


def main():
	"""Main function"""
	with open("test3.nmea", "r", encoding="utf-8") as f:
		lines = f.readlines()
	parseAndPublishLines(lines)


if __name__ == "__main__":
	main()
