from datetime import timedelta
import os
from typing import Any, Callable
import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from pynmeagps import NMEAReader, NMEAMessage
from config import Config
from gnss.nmea import GnssData, updateGnssDataWithMessage


def createMqttSubscriberClient(
	config: Config, onNewDataCallback: Callable[[bytes, GnssData], None]
) -> MqttClient:
	"""Create the subscriber MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = createSubscriberCallback(
		onNewDataCallback, timedelta(seconds=int(config.satelliteTTL))
	)

	mqttClient.connect(config.mqttHost, config.mqttPort)
	mqttClient.subscribe("gnss/rawMessages")
	mqttClient.loop_start()

	return mqttClient


def createMqttPublisherClient(config: Config) -> MqttClient:
	"""Create the publisher MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2, client_id="publisher")

	publisherPassword = os.environ.get("GNSS_PUBLISHER_PASSWORD")
	if publisherPassword:
		mqttClient.username_pw_set("gnssreceiver", publisherPassword)

	mqttClient.connect(config.mqttHost, config.mqttPort)
	mqttClient.loop_start()

	return mqttClient


def createSubscriberCallback(
	onNewDataCallback: Callable[[bytes, GnssData], None], satelliteTTL: timedelta
) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT subscriber client to handle incoming messages"""
	gnssData = GnssData()

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal gnssData
		nonlocal onNewDataCallback
		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage):
			return
		gnssData = updateGnssDataWithMessage(gnssData, parsedMessage, satelliteTTL)
		onNewDataCallback(message.payload, gnssData)

	return onMessage
