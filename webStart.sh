#! /usr/bin/env bash

bun install
bun run merge-map-to-continents
bun run build
cp views/map/1981_lines.geojson web/generated/borders.geojson

python3 -m web.background &
backgroundPid=$!

gunicorn -w 4 -b 0.0.0.0:2024 web.serve:app &
webPid=$!

trap "echo $backgroundPid & kill $backgroundPid & kill $webPid; exit" SIGINT

wait -n

kill $backgroundPid
kill $webPid
