from io import TextIOWrapper
from time import sleep

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from misc.config import loadConfig
from misc.mqtt import createMqttPublisher


def parseAndPublishLines(file: TextIOWrapper, mqttClient: mqtt.Client):
	"""Parse and publish lines from the file, waiting for the given delta time between each"""

	for line in file:
		data = line.split("\t")
		timeToSleep = float(data[0])
		nmeaMessage = data[1].strip()

		sleep(timeToSleep / 1)
		print(nmeaMessage)
		mqttClient.publish("gnss/rawMessages", nmeaMessage, qos=2)


def main():
	load_dotenv()
	config = loadConfig()
	mqttClient = createMqttPublisher(config.mqtt)
	with open("120k.tsv", "r", encoding="utf-8") as file:
		parseAndPublishLines(file, mqttClient)


if __name__ == "__main__":
	main()
