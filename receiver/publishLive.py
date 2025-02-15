from dotenv import load_dotenv
from paho.mqtt.client import Client as MqttClient
from pynmeagps import NMEAMessage

from misc.config import loadConfig
from misc.mqtt import createMqttPublisherClient
from receiver.serialMonitor import monitorSerial


def createPublishCallback(mqttClient: MqttClient):
	def onNewData(rawData: bytes, _: NMEAMessage):
		data = rawData.decode("utf-8").strip()
		mqttClient.publish("gnss/rawMessages", data, qos=2)

	return onNewData


def main():
	load_dotenv()
	config = loadConfig()
	client = createMqttPublisherClient(config)
	monitorSerial(createPublishCallback(client))


if __name__ == "__main__":
	main()
