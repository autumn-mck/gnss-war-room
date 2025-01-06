import os
from typing import Callable
from serial import Serial
from pynmeagps import NMEAReader, NMEAMessage


def getSerialLocation() -> str:
	"""Get the serial location of the receiver"""
	serialLocation = "/dev/ttyUSB0"  # default to linux
	if os.name == "nt":
		serialLocation = "COM4"  # on windows, COM4 is default for my receiver? although the other one defaults to COM3
	return serialLocation


def monitorSerial(onMessage: Callable[[bytes, NMEAMessage], None]):
	"""Monitor a serial stream and log NMEA data"""
	baudRate = 38400
	with Serial(getSerialLocation(), baudRate, timeout=3) as stream:
		nmr = NMEAReader(stream)
		while True:
			(rawData, parsedData) = nmr.read()
			if parsedData is not None:
				print(rawData)
				onMessage(rawData, parsedData)
