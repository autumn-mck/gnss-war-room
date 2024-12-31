from datetime import datetime
from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from pynmeagps import NMEAReader, NMEAMessage
from config import Config

from gnss.nmea import parseSatelliteInMessage
from gnss.satellite import SatelliteInView

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

def createMqttClient(config: Config, onNewDataCallback: Callable[[bytes, GnssData], None]) -> MqttClient:
	"""Create a new MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = createOnMessageCallback(onNewDataCallback)
	mqttClient.connect(config.mqttHost, config.mqttPort)
	mqttClient.subscribe("gnss/rawMessages")
	mqttClient.loop_start()
	return mqttClient

def createOnMessageCallback(onNewDataCallback: Callable[[bytes, GnssData], None]
					) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT client to handle incoming messages"""
	gnssData = GnssData()

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal gnssData
		nonlocal onNewDataCallback
		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage):
			return

		# no clue what's up with the typing here, it's fine though so ignore
		match parsedMessage.msgID:
			case "GSV":
				gnssData.satellites = updateSatellitePositions(gnssData.satellites, parsedMessage)
			case "GLL":
				gnssData.latitude = parsedMessage.lat
				gnssData.longitude = parsedMessage.lon
				gnssData.date = datetime.combine(gnssData.date, parsedMessage.time) # type: ignore
			case "RMC":
				gnssData.latitude = parsedMessage.lat
				gnssData.longitude = parsedMessage.lon

				# take the date from here and combine it with the time from GLL
				time = gnssData.date.time()
				gnssData.date = datetime.combine(gnssData.date, time) # type: ignore
			case "GGA":
				gnssData.latitude = parsedMessage.lat
				gnssData.longitude = parsedMessage.lon
				gnssData.geoidSeparation = parsedMessage.sep # type: ignore
				gnssData.altitude = parsedMessage.alt # type: ignore
				gnssData.hdop = parsedMessage.HDOP # type: ignore
				gnssData.fixQuality = parsedMessage.quality # type: ignore
			case "VTG":
				# seems useless
				pass
			case "GSA":
				# will get back to this later
				pass
			case _:
				print(f"Unknown message type: {parsedMessage.msgID}")
		onNewDataCallback(message.payload, gnssData)
	return onMessage

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

def isSameSatellite(satellite1: SatelliteInView, satellite2: SatelliteInView) -> bool:
	return satellite1.prnNumber == satellite2.prnNumber and satellite1.network == satellite2.network
