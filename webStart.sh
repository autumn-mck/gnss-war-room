#! /usr/bin/env bash

bun build ./web/script.js --outdir dist
python3 webBackground.py &
backgroundPid=$!
gunicorn -w 4 -b 0.0.0.0:2024 webApi:app
kill $backgroundPid
