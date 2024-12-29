from datetime import datetime, timedelta
from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from PyQt6.QtWidgets import QMainWindow
from pynmeagps import NMEAReader, NMEAMessage
from config import Config

from mapWindow import MapWindow
from gnss.nmea import parseSatelliteInMessage
from gnss.satellite import SatelliteInView
from polarGridWindow import PolarGridWindow
from miscStatsWindow import MiscStatsWindow
from rawMessageWindow import RawMessageWindow

def createMqttClient(windows: list[QMainWindow], config: Config) -> MqttClient:
	"""Create a new MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = createOnMessageCallback(windows)
	mqttClient.connect(config.mqttHost, config.mqttPort)
	mqttClient.subscribe("gnss/rawMessages")
	mqttClient.loop_start()
	return mqttClient

def createOnMessageCallback(windows: list[QMainWindow]) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT client to handle incoming messages"""
	latestSatellitePositions: list[SatelliteInView] = []
	lastUpdateTime = datetime.now()
	lastMessageUpdateTime = datetime.now()

	latitude = 0
	longitude = 0

	date = datetime.now()

	altitude = 0 # TODO: unit as well? seems to just give meters atm so that's what I'm assuming for now
	geoidSeparation = 0
	horizontalDilutionOfPrecision = 0
	fixQuality = 0 # https://receiverhelp.trimble.com/alloy-gnss/en-us/NMEA-0183messages_GGA.html for meanings

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal latestSatellitePositions
		nonlocal lastUpdateTime
		nonlocal lastMessageUpdateTime

		nonlocal latitude
		nonlocal longitude

		nonlocal date

		nonlocal altitude
		nonlocal geoidSeparation
		nonlocal horizontalDilutionOfPrecision
		nonlocal fixQuality
		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage):
			return

		# no clue what's up with the typing here, it's fine though so ignore
		match parsedMessage.msgID:
			case "GSV":
				latestSatellitePositions = updateSatellitePositions(latestSatellitePositions, parsedMessage)
			case "GLL":
				latitude = parsedMessage.lat
				longitude = parsedMessage.lon
				date = datetime.combine(date, parsedMessage.time) # type: ignore
			case "RMC":
				latitude = parsedMessage.lat
				longitude = parsedMessage.lon
				date = parsedMessage.date # type: ignore
				date = datetime.combine(date, parsedMessage.time) # type: ignore
			case "GGA":
				latitude = parsedMessage.lat
				longitude = parsedMessage.lon
				geoidSeparation = parsedMessage.sep # type: ignore
				altitude = parsedMessage.alt # type: ignore
				horizontalDilutionOfPrecision = parsedMessage.HDOP # type: ignore
				fixQuality = parsedMessage.quality # type: ignore
			case "VTG":
				# seems useless
				pass
			case "GSA":
				# will get back to this later
				pass
			case _:
				print(f"Unknown message type: {parsedMessage.msgID}")

		# limit how often we update the windows, otherwise pyqt mostly freezes
		timeSinceLastRawMessageUpdate = datetime.now() - lastMessageUpdateTime
		if timeSinceLastRawMessageUpdate < timedelta(seconds=0.01):
			return

		for window in windows:
			if isinstance(window, RawMessageWindow):
				window.onNewData(message.payload)
		lastMessageUpdateTime = datetime.now()

		timeSinceLastUpdate = datetime.now() - lastUpdateTime
		if timeSinceLastUpdate < timedelta(seconds=0.5):
			return
		lastUpdateTime = datetime.now()

		for window in windows:
			match window:
				case MapWindow():
					window.onNewData(latestSatellitePositions, latitude, longitude)
				case PolarGridWindow():
					window.onNewData(latestSatellitePositions)
				case MiscStatsWindow():
					window.onNewData(latestSatellitePositions,
						latitude,
						longitude,
						date,
						altitude,
						geoidSeparation,
						horizontalDilutionOfPrecision,
						fixQuality)
				case RawMessageWindow():
					# is updated above
					pass
				case _:
					print("Unknown window type")
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
