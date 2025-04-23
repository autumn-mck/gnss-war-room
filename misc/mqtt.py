import json
import os
import socket
import time
from datetime import datetime, timedelta
from typing import Any, Callable

import paho.mqtt.enums as mqttEnums
from paho.mqtt.client import Client as MqttClient
from paho.mqtt.client import MQTTMessage
from pynmeagps import NMEAMessage, NMEAReader

from gnss.nmea import ADSBData, GnssData, updateADSBDataWithMessage, updateGnssDataWithMessage
from misc.config import Config, MqttConfig
from misc.scrape import gpsCsvToDict, tryLoadCachedGpsJam


def figureOutPublishingConfig(config: Config):
	if len(config.multiTrackBroadcasting) > 0:
		return config.multiTrackBroadcasting
	return [config.mqtt]


def createMqttSubscriber(
	config: Config, onNewData: Callable[[bytes, GnssData, ADSBData], None]
) -> MqttClient:
	"""Create the subscriber MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)
	mqttClient.on_message = callbackOnMessage(
		onNewData,
		timedelta(seconds=int(config.satelliteTTL)),
		timedelta(seconds=int(config.flightTTL)),
	)

	mqttClient.on_disconnect = reconnectOnDisconnect
	mqttClient.on_connect = subscribeOnConnect

	try:
		mqttClient.connect(config.mqtt.host, config.mqtt.port)
		mqttClient.loop_start()
	except ConnectionRefusedError:
		print("Error! Unable to connect to MQTT broker. Don't Panic!")
		retryConnect(mqttClient, config.mqtt)
	return mqttClient


def createMqttPublishers(configs: list[MqttConfig], useragent: str) -> list[MqttClient]:
	"""Create on or more publisher MQTT clients"""

	passwordEnvPrefix = ""
	if useragent == "adsbreceiver":
		passwordEnvPrefix = "ADSB"
	elif useragent == "gnssreceiver":
		passwordEnvPrefix = "GNSS"
	else:
		raise ValueError(f"Unknown useragent: {useragent}")

	if len(configs) > 1:
		passwords = json.loads(os.environ.get(f"{passwordEnvPrefix}_MULTI_TRACK_PASSWORDS") or "[]")
	else:
		passwords = [os.environ.get(f"{passwordEnvPrefix}_PUBLISHER_PASSWORD") or ""]

	publishers = []
	for config, password in zip(configs, passwords, strict=False):
		publishers.append(createMqttPublisher(config, password, useragent))

	return publishers


def createMqttPublisher(config: MqttConfig, password: str, useragent: str) -> MqttClient:
	"""Create a single publisher MQTT client with the given configuration and password"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2, client_id=useragent)
	mqttClient.username_pw_set(useragent, password)

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


def subscribeOnConnect(client: MqttClient, *_args: Any, **_kwargs: Any):
	client.subscribe("gnss/rawMessages", qos=0)
	client.subscribe("adsb/rawMessages", qos=0)
	client.loop_start()


def reconnectOnDisconnect(client: MqttClient, *_args: Any, **_kwargs: Any):
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


def callbackOnMessage(
	onNewData: Callable[[bytes, GnssData, ADSBData], None],
	satelliteTTL: timedelta,
	flightTTL: timedelta,
) -> Callable[[MqttClient, Any, MQTTMessage], None]:
	"""Create a callback for the MQTT subscriber client to handle incoming messages"""
	gnssData = GnssData()
	gpsJamData: dict[str, tuple[int, int]] = {}
	adsbData = ADSBData()

	def onMessage(_client: MqttClient, _userdata: Any, message: MQTTMessage):
		nonlocal gnssData
		nonlocal gpsJamData
		nonlocal adsbData
		nonlocal onNewData

		match message.topic:
			case "gnss/rawMessages":
				onNewGnssData(message.payload, gnssData, gpsJamData, satelliteTTL)
				gpsJamStartDate = datetime.fromisoformat("2022-02-15")
				if not gpsJamData and gnssData.date > gpsJamStartDate:
					csv = tryLoadCachedGpsJam(gnssData.date)
					gpsJamData = gpsCsvToDict(csv)

			case "adsb/rawMessages":
				onNewAdsbData(message.payload, adsbData, flightTTL)

			case _:
				print(f"Unknown topic: {message.topic}")

		onNewData(message.payload, gnssData, adsbData)

	return onMessage


def onNewGnssData(
	rawMessage: bytes,
	gnssData: GnssData,
	gpsJamData: dict[str, tuple[int, int]],
	satelliteTTL: timedelta,
):
	"""Handle a new GNSS message"""
	parsedMessage = NMEAReader.parse(rawMessage)
	if not isinstance(parsedMessage, NMEAMessage):
		return
	gnssData = updateGnssDataWithMessage(gnssData, parsedMessage, satelliteTTL, gpsJamData)


def onNewAdsbData(rawMessage: bytes, adsbData: ADSBData, flightTTL: timedelta):
	"""Handle a new ADS-B message"""
	try:
		parsedMessage = json.loads(rawMessage)
		updateADSBDataWithMessage(adsbData, parsedMessage, flightTTL)
	except json.JSONDecodeError:
		print("Failed to decode ADS-B message")
