import os
from io import TextIOWrapper
from datetime import datetime
from serial import Serial
from pynmeagps import NMEAReader

def getSerialLocation() -> str:
	"""Get the serial location of the receiver"""
	serialLocation = '/dev/ttyUSB0' # default to linux
	if os.name == 'nt':
		serialLocation = 'COM4' # on windows, COM4 is default for my receiver? although the other one defaults to COM3
	return serialLocation

def decodeAndFormatLine(rawData: bytes) -> str:
	"""Decode a line of NMEA data and format it"""
	message = rawData.decode('utf-8')
	message = message.strip()
	logExactTimestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
	message = f"{logExactTimestamp}\t{message}\n"
	return message

def monitorAndLog(stream: Serial, logFile: TextIOWrapper, linesToLog: int):
	"""Monitor a serial stream and log NMEA data"""
	nmr = NMEAReader(stream)
	for _ in range(linesToLog):
		rawData, parsedData = nmr.read()
		if parsedData is not None:
			strData = decodeAndFormatLine(rawData)
			print(strData)
			logFile.write(strData)

def main():
	linesToLog = 50000
	baudRate = 38400
	with Serial(getSerialLocation(), baudRate, timeout=3) as stream:
		with open('test.nmea', 'w', encoding='utf-8') as logFile:
			monitorAndLog(stream, logFile, linesToLog)

if __name__ == "__main__":
	main()
