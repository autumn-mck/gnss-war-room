from datetime import datetime
from time import sleep

# parsing test.nmea
with open('test.nmea', 'r') as f:
    lines = f.readlines()

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