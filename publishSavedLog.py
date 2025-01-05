from datetime import datetime
from time import sleep
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from mqtt import createMqttPublisherClient
from config import loadConfig


def parseAndPublishLines(lines: list[str], mqttClient: mqtt.Client):
	"""Parse a list of lines, waiting for the timestamp to pass"""
	lastTimestamp = None

	for line in lines:
		data = line.split("\t")
		timestamp = data[0]
		nmeaMessage = data[1].strip()
		parsedTimestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

		if lastTimestamp is not None:
			delta = parsedTimestamp - lastTimestamp
			sleep(delta.total_seconds() / 1)
		print(nmeaMessage)
		mqttClient.publish("gnss/rawMessages", nmeaMessage, qos=0)
		lastTimestamp = parsedTimestamp


def main():
	"""Main function"""
	load_dotenv()
	config = loadConfig()
	mqttClient = createMqttPublisherClient(config)
	with open("test.nmea", "r", encoding="utf-8") as f:
		lines = f.readlines()
	parseAndPublishLines(lines, mqttClient)


if __name__ == "__main__":
	main()
