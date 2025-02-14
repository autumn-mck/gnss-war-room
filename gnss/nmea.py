from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any
import h3
from pynmeagps import NMEAMessage
from gnss.satellite import SatelliteInView, isSameSatellite


@dataclass
class GnssData:
	"""Data from GNSS receiver"""

	satellites: list[SatelliteInView] = field(default_factory=list)
	latitude: float = 0
	longitude: float = 0
	date: datetime = datetime.fromtimestamp(0)
	lastRecordedTime: datetime = datetime.fromtimestamp(0)
	altitude: float = 0
	altitudeUnit: str = "M"
	geoidSeparation: float = 0
	geoidSeparationUnit: str = "M"
	pdop: float = 0
	hdop: float = 0
	vdop: float = 0
	interference: float = 0
	fixQuality: int = 0
	"""https://receiverhelp.trimble.com/alloy-gnss/en-us/NMEA-0183messages_GGA.html for meanings"""

	def toJSON(self) -> dict[str, Any]:
		return {
			"latitude": self.latitude,
			"longitude": self.longitude,
			"date": self.date.isoformat(),
			"altitude": self.altitude,
			"geoidSeparation": self.geoidSeparation,
			"pdop": self.pdop,
			"hdop": self.hdop,
			"vdop": self.vdop,
			"fixQuality": self.fixQuality,
			"satellites": [
				satellite.toJSON(self.latitude, self.longitude) for satellite in self.satellites
			],
		}


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
			snr=tryParseFloat(getattr(parsedData, f"cno_0{satNum+1}")),
			lastSeen=updateTime,
			previousPositions=[
				(
					tryParseFloat(getattr(parsedData, f"elv_0{satNum+1}")),
					tryParseFloat(getattr(parsedData, f"az_0{satNum+1}")),
				)
			],
		)
		for satNum in range(3)
		if hasattr(parsedData, f"svid_0{satNum+1}")
	]


def tryParseFloat(string: str):
	"""Try parse the given string as a float, return if successful, otherwise return 0"""
	if str is None:
		return 0
	try:
		return float(string)
	except ValueError:
		return 0


def updateGnssDataWithMessage(
	gnssData: GnssData,
	message: NMEAMessage,
	satelliteTTL: timedelta,
	h3Dict: dict[str, tuple[int, int]],
):
	"""Update the gnss data with the new data from a message"""
	# no clue what's up with the typing here, it's fine though so ignore
	match message.msgID:
		case "GSV":
			gnssData.satellites = updateSatellitePositions(
				gnssData.satellites, message, gnssData.date, satelliteTTL
			)
			if gnssData.date - gnssData.lastRecordedTime > timedelta(seconds=1200):
				gnssData.lastRecordedTime = gnssData.date
				gnssData.satellites = updateSaltellitePreviousPositions(gnssData.satellites)
		case "GLL":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.date = datetime.combine(gnssData.date, message.time)  # type: ignore
		case "RMC":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.date = datetime.combine(message.date, message.time)  # type: ignore

			if h3Dict:
				h3Cell = h3.latlng_to_cell(message.lat, message.lon, 4)
				if h3Cell in h3Dict:
					countGood, countBad = h3Dict[h3Cell]
					gnssData.interference = countBad / (countGood + countBad) * 100
		case "GGA":
			gnssData.latitude = message.lat
			gnssData.longitude = message.lon
			gnssData.geoidSeparation = message.sep  # type: ignore
			gnssData.geoidSeparationUnit = message.sepUnit  # type: ignore
			gnssData.altitude = message.alt  # type: ignore
			gnssData.altitudeUnit = message.altUnit  # type: ignore
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


def updateSaltellitePreviousPositions(satellites: list[SatelliteInView]) -> list[SatelliteInView]:
	for satellite in satellites:
		satellite.previousPositions.append((satellite.elevation, satellite.azimuth))
	return satellites


def updateSatellitePositions(
	satellites: list[SatelliteInView],
	nmeaSentence: NMEAMessage,
	updateTime: datetime,
	satelliteTTL: timedelta,
) -> list[SatelliteInView]:
	"""Update the satellite positions in the windows"""
	newSatelliteData = parseSatelliteInMessage(nmeaSentence, updateTime)
	# update existing satellites
	for i, oldData in enumerate(satellites):
		matchingNewData = next(
			(newData for newData in newSatelliteData if isSameSatellite(newData, oldData)), None
		)
		if matchingNewData is not None:
			matchingNewData.previousPositions = oldData.previousPositions
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
