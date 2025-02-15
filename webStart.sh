#! /usr/bin/env bash

bun install
bunx mapshaper -i views/map/1981_polygons.geojson snap snap-interval=0.1 -dissolve2 -o precision=0.1 web/generated/continents.geojson
cp views/map/1981_lines.geojson web/generated/borders.geojson
bun build ./web/script.ts --outdir dist

python3 -m web.background &
backgroundPid=$!

gunicorn -w 4 -b 0.0.0.0:2024 web.serve:app &
webPid=$!

trap "echo $backgroundPid & kill $backgroundPid & kill $webPid; exit" SIGINT

wait -n

kill $backgroundPid
kill $webPid
