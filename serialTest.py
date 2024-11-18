from serial import Serial
from pynmeagps import NMEAReader

LINES_TO_LOG = 500

with Serial('/dev/ttyUSB0', 38400, timeout=3) as stream:
	nmr = NMEAReader(stream)
	with open('test.nmea', 'w', encoding='utf-8') as logFile:
		for _ in range(LINES_TO_LOG):
			raw_data, parsed_data = nmr.read()
			if parsed_data is not None:
				print(raw_data)
				logFile.write(raw_data.decode('utf-8'))
