import time
from typing import Any

import paho.mqtt.enums as mqttEnums
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from paho.mqtt.client import Client as MqttClient
from paho.mqtt.client import MQTTMessage

from misc.config import Config, loadConfig
from misc.mqtt import createMqttPublisher


def main():
	"""Send numerous messages to the MQTT broker and measure how long each of these 'ping's takes"""
	load_dotenv()
	config = loadConfig()
	publisher = createMqttPublisher(config)
	subscriber = createMqttClient(config)

	times: list[float] = []
	for i in range(100_000):
		timeMs = sendReceiveMessage(publisher, subscriber, f"who up webbing they fish {i}")
		print(timeMs)
		if timeMs < 80:
			times.append(timeMs)

	plt.hist(times, bins=100)
	plt.show()


def createMqttClient(config: Config) -> MqttClient:
	"""Create the subscriber MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)

	mqttClient.on_connect = print
	mqttClient.on_message = print
	mqttClient.connect(config.mqttHost, config.mqttPort)
	mqttClient.subscribe("gnss/rawMessages", qos=0)
	mqttClient.loop_start()
	return mqttClient


def sendReceiveMessage(publisher: MqttClient, subscriber: MqttClient, message: str) -> float:
	"""Measure the time taken for a message to be sent and received"""
	sentTime = time.time()
	receivedTime = None

	def onMessage(_client: MqttClient, _userdata: Any, _message: MQTTMessage):
		nonlocal receivedTime
		receivedTime = time.time()

	subscriber.on_message = onMessage
	sentTime = time.time()
	publisher.publish("gnss/rawMessages", message, qos=0)

	while receivedTime is None:
		time.sleep(0.001)

	return (receivedTime - sentTime) * 1000


if __name__ == "__main__":
	main()
