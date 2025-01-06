from dotenv import load_dotenv
from paho.mqtt.client import Client as MqttClient
from pynmeagps import NMEAMessage
from config import loadConfig
from serialMonitor import monitorSerial
from mqtt import createMqttPublisherClient


def createPublishCallback(mqttClient: MqttClient):
	def onNewData(rawData: bytes, _: NMEAMessage):
		data = rawData.decode("utf-8").strip()
		mqttClient.publish("gnss/rawMessages", data, qos=0)

	return onNewData


def main():
	load_dotenv()
	config = loadConfig()
	client = createMqttPublisherClient(config)
	monitorSerial(createPublishCallback(client))


if __name__ == "__main__":
	main()
