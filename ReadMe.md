# GNSS and Precision Time War Room

## Setup

Create a virtual environment: `python -m venv .venv` and activate it: `source .venv/bin/activate`

Install dependencies: `pip install -r requirements.txt`

### If running MQTT locally

Set a password for publishing to the MQTT broker: `podman exec mosquitto mosquitto_passwd -b /etc/mosquitto/passwd gnssreceiver <password>`

This password must be set in the `RECEIVER_MQTT_PASSWORD` environment variable in the `.env` file.

### If running MQTT on a remote server

Edit `config.json5` and set `mqttHost` to the hostname of the remote server. You will also need to set the `RECEIVER_MQTT_PASSWORD` environment variable.

## Running

To display the main PyQt GUI: `python main.py`

To run the web frontend: `bash webStart.sh` (will default to port 2024)
