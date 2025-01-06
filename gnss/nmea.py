from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pynmeagps import NMEAMessage
from gnss.satellite import SatelliteInView, isSameSatellite


@dataclass
class GnssData:
	"""Data from GNSS receiver"""

	satellites: list[SatelliteInView] = field(default_factory=list)
	latitude: float = 0
	longitude: float = 0
	date: datetime = datetime.fromtimestamp(0)
	altitude: float = 0
	geoidSeparation: float = 0
	pdop: float = 0
	hdop: float = 0
	vdop: float = 0
	fixQuality: int = 0
	"""https://receiverhelp.trimble.com/alloy-gnss/en-us/NMEA-0183messages_GGA.html for meanings"""


def filterMessagesToType(nmeaMessages: list[NMEAMessage], messageType: str) -> list[NMEAMessage]:
	return [parsedData for parsedData in nmeaMessages if parsedData.msgID == messageType]


def parseSatelliteInMessage(parsedData: NMEAMessage, updateTime: datetime) -> list[SatelliteInView]:
	"""Parse a GSV message into a list of SatelliteInView objects"""
	if parsedData.msgID != "GSV":
		raise ValueError(f"Expected GSV message, got {parsedData.msgID}")

	return [
		SatelliteInView(
			prnNumber=getattr(parsedData, f"svid_0{satNum+1}"),
			network=parsedData.talker,
			elevation=tryParseFloat(getattr(parsedData, f"elv_0{satNum+1}")),
			azimuth=tryParseFloat(getattr(parsedData, f"az_0{satNum+1}")),
			snr=getattr(parsedData, f"cno_0{satNum+1}"),
			lastSeen=updateTime,
		)
		for satNum in range(3)
		if hasattr(parsedData, f"svid_0{satNum+1}")
	]


def tryParseFloat(string: str):
	if str is None:
		return 0
	try:
		return float(string)
	except ValueError:
		return 0


def updateGnssDataWithMessage(gnssData: GnssData, message: NMEAMessage):
	"""Update the gnss data with the new data from a message"""
	# no clue what's up with the typing here, it's fine though so ignore
	match message.msgID:
		case "GSV":
			gnssData.satellites = updateSatellitePositions(
				gnssData.satellites, message, gnssData.date
			)
		case "GLL":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.date = datetime.combine(gnssData.date, message.time)  # type: ignore
		case "RMC":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon

			# take the date from here and combine it with the time from GLL
			time = gnssData.date.time()
			gnssData.date = datetime.combine(message.date, time)  # type: ignore
		case "GGA":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.geoidSeparation = message.sep  # type: ignore
			gnssData.altitude = message.alt  # type: ignore
			gnssData.hdop = message.HDOP  # type: ignore
			gnssData.fixQuality = message.quality  # type: ignore
		case "VTG":
			# seems useless
			pass
		case "GSA":
			gnssData.pdop = message.PDOP  # type: ignore
			gnssData.hdop = message.HDOP  # type: ignore
			gnssData.vdop = message.VDOP  # type: ignore
		case _:
			print(f"Unknown message type: {message.msgID}")
	return gnssData


def updateSatellitePositions(
	satellites: list[SatelliteInView],
	nmeaSentence: NMEAMessage,
	updateTime: datetime,
	satelliteTTL: timedelta = timedelta(seconds=30),
) -> list[SatelliteInView]:
	"""Update the satellite positions in the windows"""
	newSatelliteData = parseSatelliteInMessage(nmeaSentence, updateTime)
	# update existing satellites
	for i, oldData in enumerate(satellites):
		matchingNewData = next(
			(newData for newData in newSatelliteData if isSameSatellite(newData, oldData)), None
		)
		if matchingNewData is not None:
			satellites[i] = matchingNewData

	# remove satellites that haven't been seen in a while
	satellites = [
		satellite for satellite in satellites if satellite.lastSeen + satelliteTTL > updateTime
	]

	# add new satellites
	newSatellites = [
		newData
		for newData in newSatelliteData
		if not any(isSameSatellite(newData, oldData) for oldData in satellites)
	]
	satellites.extend(newSatellites)

	return satellites
