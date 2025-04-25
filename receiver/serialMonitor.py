from collections.abc import Callable

from pynmeagps import NMEAMessage, NMEAReader
from serial import Serial

from misc.config import GnssConfig


def monitorSerial(onMessage: Callable[[bytes, NMEAMessage], None], config: GnssConfig):
	"""Monitor a serial stream and log NMEA data"""
	with Serial(config.serialPort, config.baudRate, timeout=3) as stream:
		nmr = NMEAReader(stream)
		while True:
			(rawData, parsedData) = nmr.read()
			if parsedData is not None:
				print(rawData)
				onMessage(rawData, parsedData)
