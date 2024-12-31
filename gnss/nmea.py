from datetime import datetime
from pynmeagps import NMEAMessage
from gnss.satellite import SatelliteInView, isSameSatellite

class GnssData:
	"""Data from GNSS receiver"""
	satellites: list[SatelliteInView]
	latitude: float
	longitude: float
	date: datetime
	altitude: float
	geoidSeparation: float
	hdop: float
	fixQuality: int
	"""https://receiverhelp.trimble.com/alloy-gnss/en-us/NMEA-0183messages_GGA.html for meanings"""

	def __init__(self):
		self.satellites = []
		self.latitude = 0
		self.longitude = 0
		self.date = datetime.now()
		self.altitude = 0
		self.geoidSeparation = 0
		self.hdop = 0
		self.fixQuality = 0

def filterMessagesToType(nmeaMessages: list[NMEAMessage], messageType: str) -> list[NMEAMessage]:
	return [
		parsedData for parsedData in nmeaMessages
		if parsedData.msgID == messageType
	]

def parseSatelliteInMessage(parsedData: NMEAMessage) -> list[SatelliteInView]:
	"""Parse a GSV message into a list of SatelliteInView objects"""
	if parsedData.msgID != 'GSV':
		raise ValueError(f"Expected GSV message, got {parsedData.msgID}")

	return [
		SatelliteInView(
			prnNumber=getattr(parsedData, f'svid_0{satNum+1}'),
			network=parsedData.talker,
			elevation=getattr(parsedData, f'elv_0{satNum+1}'),
			azimuth=getattr(parsedData, f'az_0{satNum+1}'),
			snr=getattr(parsedData, f'cno_0{satNum+1}')
		)
		for satNum in range(3)
		if hasattr(parsedData, f'svid_0{satNum+1}')
	]

def updateGnssDataWithMessage(gnssData: GnssData, message: NMEAMessage):
	"""Update the gnss data with the new data from a message"""
	# no clue what's up with the typing here, it's fine though so ignore
	match message.msgID:
		case "GSV":
			gnssData.satellites = updateSatellitePositions(gnssData.satellites, message)
		case "GLL":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.date = datetime.combine(gnssData.date, message.time) # type: ignore
		case "RMC":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon

			# take the date from here and combine it with the time from GLL
			time = gnssData.date.time()
			gnssData.date = datetime.combine(gnssData.date, time) # type: ignore
		case "GGA":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.geoidSeparation = message.sep # type: ignore
			gnssData.altitude = message.alt # type: ignore
			gnssData.hdop = message.HDOP # type: ignore
			gnssData.fixQuality = message.quality # type: ignore
		case "VTG":
			# seems useless
			pass
		case "GSA":
			# will get back to this later
			pass
		case _:
			print(f"Unknown message type: {message.msgID}")
	return gnssData

def updateSatellitePositions(satellites: list[SatelliteInView], nmeaSentence: NMEAMessage) -> list[SatelliteInView]:
	"""Update the satellite positions in the windows"""
	newSatelliteData = parseSatelliteInMessage(nmeaSentence)
	# update existing satellites
	for i, oldData in enumerate(satellites):
		matchingNewData = next((newData for newData in newSatelliteData if isSameSatellite(newData, oldData)), None)
		if matchingNewData is not None:
			satellites[i] = matchingNewData

	# add new satellites
	newSatellites = [
		newData
		for newData in newSatelliteData
		if not any(isSameSatellite(newData, oldData) for oldData in satellites)
	]
	satellites.extend(newSatellites)

	return satellites
