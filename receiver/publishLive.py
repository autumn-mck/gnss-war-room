from dotenv import load_dotenv
from paho.mqtt.client import Client as MqttClient
from pynmeagps import NMEAMessage

from misc.config import loadConfig
from misc.mqtt import createMqttPublishers, figureOutPublishingConfig
from receiver.serialMonitor import monitorSerial


def createPublishCallback(mqttClients: list[MqttClient]):
	"""Create a function to publish any time a message is received"""

	def publishMessage(rawData: bytes, _: NMEAMessage):
		data = rawData.decode("utf-8").strip()
		for mqttClient in mqttClients:
			mqttClient.publish("gnss/rawMessages", data, qos=2)

	return publishMessage


def main():
	"""Publish the live GNSS data"""
	load_dotenv()
	config = loadConfig()
	mqttConfig = figureOutPublishingConfig(config)

	clients = createMqttPublishers(mqttConfig)
	onMessage = createPublishCallback(clients)
	monitorSerial(onMessage, config.gnss)


if __name__ == "__main__":
	main()
