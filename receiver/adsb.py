import json
import os
from datetime import datetime
from io import TextIOWrapper
from time import sleep

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from misc.config import loadConfig
from misc.mqtt import createMqttPublishers, figureOutPublishingConfig


def parseAndPublishLines(file: TextIOWrapper, mqttClients: list[mqtt.Client]):
	"""Parse and publish lines from the file, waiting for the given delta time between each"""

	startTime = None

	speedMult = float(os.environ.get("ADSB_SPEED_MULT") or 1)

	for line in file:
		parsedData = json.loads(line)

		time = datetime.strptime(parsedData["0"], "%Y-%m-%dT%H:%M:%S.%fZ")
		if startTime is None:
			startTime = time

		timeToSleep = (time - startTime).total_seconds()
		sleep(timeToSleep / speedMult)
		startTime = time

		print(parsedData)
		for mqttClient in mqttClients:
			mqttClient.publish("adsb/rawMessages", line, qos=0)


def main():
	"""Publish the prerecorded ADS-B messages"""
	load_dotenv()
	config = loadConfig()
	mqttConfig = figureOutPublishingConfig(config)
	mqttClients = createMqttPublishers(mqttConfig, "adsbreceiver")

	with open("adsb-1.txt", "r", encoding="utf-8") as file:
		parseAndPublishLines(file, mqttClients)


if __name__ == "__main__":
	main()
