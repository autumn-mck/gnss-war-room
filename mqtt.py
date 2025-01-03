from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from pynmeagps import NMEAReader, NMEAMessage
from config import Config
from gnss.nmea import GnssData, updateGnssDataWithMessage


def createMqttClient(
	config: Config, onNewDataCallback: Callable[[bytes, GnssData], None]
) -> MqttClient:
	"""Create a new MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = createOnMessageCallback(onNewDataCallback)
	mqttClient.connect(config.mqttHost, config.mqttPort)
	mqttClient.subscribe("gnss/rawMessages")
	mqttClient.loop_start()
	return mqttClient


def createOnMessageCallback(
	onNewDataCallback: Callable[[bytes, GnssData], None],
) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT client to handle incoming messages"""
	gnssData = GnssData()

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal gnssData
		nonlocal onNewDataCallback
		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage):
			return
		gnssData = updateGnssDataWithMessage(gnssData, parsedMessage)
		onNewDataCallback(message.payload, gnssData)

	return onMessage
