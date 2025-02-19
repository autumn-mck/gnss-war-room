from time import sleep

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from misc.config import loadConfig
from misc.mqtt import createMqttPublisherClient


def parseAndPublishLines(lines: list[str], mqttClient: mqtt.Client):
	"""Parse a list of lines, waiting for the timestamp to pass"""

	for line in lines:
		data = line.split("\t")
		timeToSleep = float(data[0])
		nmeaMessage = data[1].strip()

		sleep(timeToSleep / 1)
		print(nmeaMessage)
		mqttClient.publish("gnss/rawMessages", nmeaMessage, qos=2)


def main():
	"""Main function"""
	load_dotenv()
	config = loadConfig()
	mqttClient = createMqttPublisherClient(config)
	with open("120k.tsv", "r", encoding="utf-8") as f:
		lines = f.readlines()
	parseAndPublishLines(lines, mqttClient)


if __name__ == "__main__":
	main()
