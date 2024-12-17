# GNSS and Precision Time War Room

## Setup

Set a password for publishing to the MQTT broker: `podman exec mosquitto mosquitto_passwd -b /etc/mosquitto/passwd gnssreceiver <password>`

This password must be set in the `RECEIVER_MQTT_PASSWORD` environment variable in the `.env` file.