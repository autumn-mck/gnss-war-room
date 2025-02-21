from io import TextIOWrapper
from time import sleep

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from misc.config import loadConfig
from misc.mqtt import createMqttPublishers, figureOutPublishingConfig


def parseAndPublishLines(file: TextIOWrapper, mqttClients: list[mqtt.Client]):
	"""Parse and publish lines from the file, waiting for the given delta time between each"""

	for line in file:
		data = line.split("\t")
		timeToSleep = float(data[0])
		nmeaMessage = data[1].strip()

		sleep(timeToSleep / 1)
		print(nmeaMessage)
		for mqttClient in mqttClients:
			mqttClient.publish("gnss/rawMessages", nmeaMessage, qos=2)


def main():
	"""Publish the prerecorded messages"""
	load_dotenv()
	config = loadConfig()
	mqttConfig = figureOutPublishingConfig(config)
	mqttClients = createMqttPublishers(mqttConfig)

	with open("120k.tsv", "r", encoding="utf-8") as file:
		parseAndPublishLines(file, mqttClients)


if __name__ == "__main__":
	main()
