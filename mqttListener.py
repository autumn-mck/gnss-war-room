import paho.mqtt.client as mqtt
import paho.mqtt.enums as mqttEnums

def onMessage(_client, _userdata, message):
	print(message.topic + " " + str(message.payload))

def onDisconnect(client, _userdata, _rc, _reasonCode, _properties):
	client.reconnect()

mqttClient = mqtt.Client(mqttEnums.CallbackAPIVersion.VERSION2)
mqttClient.enable_logger()

mqttClient.on_message = onMessage
mqttClient.on_disconnect = onDisconnect

mqttClient.connect("localhost")
mqttClient.subscribe("gnss/rawMessages")
mqttClient.loop_forever()
