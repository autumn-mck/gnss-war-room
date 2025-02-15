from io import TextIOWrapper
from datetime import datetime
from pynmeagps import NMEAMessage
from receiver.serialMonitor import monitorSerial


def createWriteCallback(logFile: TextIOWrapper):
	"""Create function to write new messages with timestamp to the log"""

	def onNewData(rawData: bytes, _: NMEAMessage):
		message = rawData.decode("utf-8").strip()
		logExactTimestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
		message = f"{logExactTimestamp}\t{message}\n"
		logFile.write(message)

	return onNewData


def main():
	with open("test.nmea", "w", encoding="utf-8") as logFile:
		monitorSerial(createWriteCallback(logFile))


if __name__ == "__main__":
	main()
