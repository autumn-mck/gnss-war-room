#! /usr/bin/env bash

python3 webBackground.py &
gunicorn -w 4 -b 0.0.0.0:2024 webApi:app
