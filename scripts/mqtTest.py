import time
from typing import Any

import paho.mqtt.enums as mqttEnums
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from paho.mqtt.client import Client as MqttClient
from paho.mqtt.client import MQTTMessage

from misc.config import MqttConfig, loadConfig
from misc.mqtt import createMqttPublishers


def main():
	"""Send numerous messages to the MQTT broker and measure how long each of these 'ping's takes"""
	load_dotenv()
	config = loadConfig()
	publisher = createMqttPublishers([config.mqtt])[0]
	subscriber = createMqttClient(config.mqtt)

	with open("120k.nmea", "r", encoding="utf-8") as f:
		lines = f.readlines()

	times: list[float] = []
	numMessages = 10_000
	for i in range(numMessages):
		timeMs = sendReceiveMessage(publisher, subscriber, lines[i])
		print(f"{(i / numMessages * 100):.2f}% done")
		times.append(timeMs)

	print(f"Median: {calcPercentile(times, 50):.2f}ms")
	print(f"90th percentile: {calcPercentile(times, 90):.2f}ms")
	print(f"99th percentile: {calcPercentile(times, 99):.2f}ms")
	print(f"99.9th percentile: {calcPercentile(times, 99.9):.2f}ms")
	upperBound = calcPercentile(times, 99.95)

	fig = plt.figure()
	axs = fig.subplots(1, 1)
	plt.hist(times, bins=500, cumulative=True, range=(0, upperBound), density=True)

	axs.set_title("RTT for MQTT messages (Different network)")
	axs.set_xlabel("Time (ms)")
	axs.set_ylabel("Probability message arrived (cumulative)")

	axs.set_xlim(0, upperBound)
	axs.set_ymargin(0.03)

	plt.show()


def calcPercentile(times: list[float], percentile: float) -> float:
	sortedTimes = sorted(times)
	index = int(len(sortedTimes) * (percentile / 100))
	return sortedTimes[index]


def createMqttClient(config: MqttConfig) -> MqttClient:
	"""Create the subscriber MQTT client"""
	mqttClient = MqttClient(mqttEnums.CallbackAPIVersion.VERSION2)

	mqttClient.on_connect = print
	mqttClient.on_message = print
	mqttClient.connect(config.host, config.port)
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
	publisher.publish("gnss/rawMessages", message, qos=2)

	while receivedTime is None:
		time.sleep(0.001)

	return (receivedTime - sentTime) * 1000


if __name__ == "__main__":
	main()
