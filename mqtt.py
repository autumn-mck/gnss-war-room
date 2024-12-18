from datetime import datetime, timedelta
from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from PyQt6.QtWidgets import QMainWindow
from pynmeagps import NMEAReader, NMEAMessage

from mapWindow import MapWindow
from gnss.nmea import parseSatelliteInMessage
from gnss.satellite import SatelliteInView
from polarGridWindow import PolarGridWindow

def createMqttClient(windows: list[QMainWindow]) -> MqttClient:
	"""Create a new MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = createOnMessageCallback(windows)
	mqttClient.connect("localhost")
	mqttClient.subscribe("gnss/rawMessages")
	mqttClient.loop_start()
	return mqttClient

def createOnMessageCallback(windows: list[QMainWindow]) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT client to handle incoming messages"""
	latestSatellitePositions: list[SatelliteInView] = []
	lastUpdateTime = datetime.now()

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal latestSatellitePositions
		nonlocal lastUpdateTime
		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage) or parsedMessage.msgID != 'GSV':
			return

		latestSatellitePositions = updateSatellitePositions(latestSatellitePositions, parsedMessage)

		timeSinceLastUpdate = datetime.now() - lastUpdateTime
		if timeSinceLastUpdate < timedelta(seconds=1):
			return
		lastUpdateTime = datetime.now()
		updateAllWindows(windows, latestSatellitePositions)

	return onMessage

def updateAllWindows(windows: list[QMainWindow], satellites: list[SatelliteInView]):
	"""Update all windows with the latest satellite positions"""
	for window in windows:
		match window:
			case MapWindow():
				window.onSatellitesReceived(satellites)
			case PolarGridWindow():
				window.onSatellitesReceived(satellites)
			case _:
				print("Unknown window type")

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
