from datetime import timedelta, datetime
import os
import time
from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient, MQTTMessage, DisconnectFlags, ConnectFlags
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.properties import Properties
from pynmeagps import NMEAReader, NMEAMessage

from misc.config import Config
from misc.scrape import tryLoadCachedGpsJam, gpsCsvToDict
from gnss.nmea import GnssData, updateGnssDataWithMessage


def createMqttSubscriberClient(
	config: Config, onNewDataCallback: Callable[[bytes, GnssData], None]
) -> MqttClient:
	"""Create the subscriber MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = createSubscriberCallback(
		onNewDataCallback, timedelta(seconds=int(config.satelliteTTL))
	)

	mqttClient.on_disconnect = onDisconnect
	mqttClient.on_connect = onConnect

	try:
		mqttClient.connect(config.mqttHost, config.mqttPort)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		print("Error! Unable to connect to MQTT broker. Don't Panic!")
		retryConnect(mqttClient, config)
	return mqttClient


def createMqttPublisherClient(config: Config) -> MqttClient:
	"""Create the publisher MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2, client_id="publisher")

	publisherPassword = os.environ.get("GNSS_PUBLISHER_PASSWORD")
	if publisherPassword:
		mqttClient.username_pw_set("gnssreceiver", publisherPassword)

	mqttClient.on_disconnect = onDisconnect
	mqttClient.on_connect = onConnect

	try:
		mqttClient.connect(config.mqttHost, config.mqttPort)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		print("Error! Unable to connect to MQTT broker. Don't Panic!")
		retryConnect(mqttClient, config)
	return mqttClient


def retryConnect(mqttClient: MqttClient, config: Config, attemptsLeft=5):
	"""Retry connecting to the MQTT broker if it fails on startup"""
	if attemptsLeft < 0:
		print("Failed to connect!")
		os.abort()

	time.sleep(1)
	print(f"Retrying, {attemptsLeft} attempts remaining.")
	try:
		mqttClient.connect(config.mqttHost, config.mqttPort)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		retryConnect(mqttClient, config, attemptsLeft - 1)


def onConnect(
	client: MqttClient, _userdata: Any, _flags: ConnectFlags, _rc: int, _properties: Properties
):
	client.subscribe("gnss/rawMessages")
	client.loop_start()


def onDisconnect(
	client: MqttClient,
	_userdata: Any,
	_disconnectFlags: DisconnectFlags,
	_reasonCode: ReasonCode,
	_properties: Properties,
):
	"""Exit the program if the MQTT broker disconnects, as attempting to reconnect doesn't seem to work"""
	print("Disconnected from MQTT broker. Don't Panic!")
	tryReconnect(client)


def tryReconnect(mqttClient: MqttClient, attemptNum=1):
	"""Attempt to reconnect to the MQTT broker if it disconnects"""
	time.sleep(1)
	print(f"Reconnecting to MQTT broker, attempt {attemptNum}")
	try:
		mqttClient.reconnect()
		print("Reconnected to MQTT broker!")
	except ConnectionRefusedError:
		tryReconnect(mqttClient, attemptNum + 1)


def createSubscriberCallback(
	onNewDataCallback: Callable[[bytes, GnssData], None], satelliteTTL: timedelta
) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT subscriber client to handle incoming messages"""
	gnssData = GnssData()
	h3Dict: dict[str, tuple[int, int]] = {}

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal gnssData
		nonlocal h3Dict
		nonlocal onNewDataCallback
		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage):
			return
		gnssData = updateGnssDataWithMessage(gnssData, parsedMessage, satelliteTTL, h3Dict)

		if not h3Dict and gnssData.date > datetime.fromisoformat("2022-02-15"):
			csv = tryLoadCachedGpsJam(gnssData.date)
			h3Dict = gpsCsvToDict(csv)

		onNewDataCallback(message.payload, gnssData)

	return onMessage
