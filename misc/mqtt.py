import json
import os
import socket
import time
from datetime import datetime, timedelta
from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient
from paho.mqtt.client import ConnectFlags, DisconnectFlags, MQTTMessage
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode
from pynmeagps import NMEAMessage, NMEAReader

from gnss.nmea import GnssData, updateGnssDataWithMessage
from misc.config import Config, MqttConfig
from misc.scrape import gpsCsvToDict, tryLoadCachedGpsJam


def figureOutPublishingConfig(config: Config):
	if len(config.multiTrackBroadcasting) > 0:
		return config.multiTrackBroadcasting
	return [config.mqtt]


def createMqttSubscriber(
	config: MqttConfig, satelliteTTL: int, onNewData: Callable[[bytes, GnssData], None]
) -> MqttClient:
	"""Create the subscriber MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = callbaackOnMessage(onNewData, timedelta(seconds=int(satelliteTTL)))

	mqttClient.on_disconnect = reconnectOnDisconnect
	mqttClient.on_connect = subscribeOnConnect

	try:
		mqttClient.connect(config.host, config.port)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		print("Error! Unable to connect to MQTT broker. Don't Panic!")
		retryConnect(mqttClient, config)
	return mqttClient


def createMqttPublishers(configs: list[MqttConfig]) -> list[MqttClient]:
	"""Create on or more publisher MQTT clients"""

	if len(configs) > 0:
		passwords = json.loads(os.environ.get("GNSS_MULTI_TRACK_PASSWORDS") or "[]")
	else:
		passwords = [os.environ.get("GNSS_PUBLISHER_PASSWORD") or ""]

	publishers = []
	for config, password in zip(configs, passwords):
		publishers.append(createMqttPublisher(config, password))

	return publishers


def createMqttPublisher(config: MqttConfig, password: str) -> MqttClient:
	"""Create a single publisher MQTT client with the given configuration and password"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2, client_id="publisher")
	mqttClient.username_pw_set("gnssreceiver", password)

	mqttClient.on_disconnect = reconnectOnDisconnect

	try:
		mqttClient.connect(config.host, config.port)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		print("Error! Unable to connect to MQTT broker. Don't Panic!")
		retryConnect(mqttClient, config)
	return mqttClient


def retryConnect(mqttClient: MqttClient, config: MqttConfig, attemptsLeft=5):
	"""Retry connecting to the MQTT broker if it fails on startup"""
	if attemptsLeft < 0:
		print("Failed to connect!")
		os.abort()

	time.sleep(1)
	print(f"Retrying, {attemptsLeft} attempts remaining.")
	try:
		mqttClient.connect(config.host, config.port)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		retryConnect(mqttClient, config, attemptsLeft - 1)


def subscribeOnConnect(
	client: MqttClient, _userdata: Any, _flags: ConnectFlags, _rc: int, _properties: Properties
):
	client.subscribe("gnss/rawMessages", qos=2)
	client.loop_start()


def reconnectOnDisconnect(
	client: MqttClient,
	_userdata: Any,
	_disconnectFlags: DisconnectFlags,
	_reasonCode: ReasonCode,
	_properties: Properties,
):
	"""Exit the program if the MQTT broker disconnects, as attempting to reconnect does not seem to
	work
	"""
	print("Disconnected from MQTT broker. Don't Panic!")
	tryReconnectAfterDisconnect(client)


def tryReconnectAfterDisconnect(mqttClient: MqttClient, attemptNum=1):
	"""Attempt to reconnect to the MQTT broker if it disconnects"""
	time.sleep(1)
	print(f"Reconnecting to MQTT broker, attempt {attemptNum}")
	try:
		mqttClient.reconnect()
		print("Reconnected to MQTT broker!")
	except ConnectionRefusedError:
		tryReconnectAfterDisconnect(mqttClient, attemptNum + 1)
	except socket.gaierror:
		tryReconnectAfterDisconnect(mqttClient, attemptNum + 1)


def callbaackOnMessage(
	onNewData: Callable[[bytes, GnssData], None], satelliteTTL: timedelta
) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT subscriber client to handle incoming messages"""
	gnssData = GnssData()
	gpsJamData: dict[str, tuple[int, int]] = {}

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal gnssData
		nonlocal gpsJamData
		nonlocal onNewData

		parsedMessage = NMEAReader.parse(message.payload)
		if not isinstance(parsedMessage, NMEAMessage):
			return
		gnssData = updateGnssDataWithMessage(gnssData, parsedMessage, satelliteTTL, gpsJamData)

		gpsJamStartDate = datetime.fromisoformat("2022-02-15")
		if not gpsJamData and gnssData.date > gpsJamStartDate:
			csv = tryLoadCachedGpsJam(gnssData.date)
			gpsJamData = gpsCsvToDict(csv)

		onNewData(message.payload, gnssData)

	return onMessage
