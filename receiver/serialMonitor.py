from typing import Callable

from pynmeagps import NMEAMessage, NMEAReader
from serial import Serial


def monitorSerial(onMessage: Callable[[bytes, NMEAMessage], None], serialLocation: str):
	"""Monitor a serial stream and log NMEA data"""
	baudRate = 38400
	with Serial(serialLocation, baudRate, timeout=3) as stream:
		nmr = NMEAReader(stream)
		while True:
			(rawData, parsedData) = nmr.read()
			if parsedData is not None:
				print(rawData)
				onMessage(rawData, parsedData)
