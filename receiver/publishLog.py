import os
from io import TextIOWrapper
from time import sleep

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from misc.config import loadConfig
from misc.mqtt import createMqttPublishers, figureOutPublishingConfig


def parseAndPublishLines(file: TextIOWrapper, mqttClients: list[mqtt.Client]):
	"""Parse and publish lines from the file, waiting for the given delta time between each"""

	speedMult = float(os.environ.get("GNSS_SPEED_MULT") or 1)

	for line in file:
		data = line.split("\t")
		timeToSleep = float(data[0])
		nmeaMessage = data[1].strip()

		sleep(timeToSleep / speedMult)
		print(nmeaMessage)
		for mqttClient in mqttClients:
			mqttClient.publish("gnss/rawMessages", nmeaMessage, qos=0)


def main():
	"""Publish the prerecorded GNSS messages"""
	load_dotenv()
	config = loadConfig()
	mqttConfig = figureOutPublishingConfig(config)
	mqttClients = createMqttPublishers(mqttConfig, "gnssreceiver")

	with open("3m.tsv", "r", encoding="utf-8") as file:
		parseAndPublishLines(file, mqttClients)


if __name__ == "__main__":
	main()
