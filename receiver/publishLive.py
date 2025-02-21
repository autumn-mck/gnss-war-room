from dotenv import load_dotenv
from paho.mqtt.client import Client as MqttClient
from pynmeagps import NMEAMessage

from misc.config import loadConfig
from misc.mqtt import createMqttPublisher
from receiver.serialMonitor import monitorSerial


def createPublishCallback(mqttClient: MqttClient):
	def publishMessage(rawData: bytes, _: NMEAMessage):
		data = rawData.decode("utf-8").strip()
		mqttClient.publish("gnss/rawMessages", data, qos=2)

	return publishMessage


def main():
	load_dotenv()
	config = loadConfig()
	client = createMqttPublisher(config.mqtt)
	onMessage = createPublishCallback(client)
	monitorSerial(onMessage, config.gnss)


if __name__ == "__main__":
	main()
