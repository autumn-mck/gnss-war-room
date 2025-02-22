import json
import os
import threading
import time
from datetime import datetime

from dotenv import load_dotenv

from font.fetch import fetchFontRomsIfNeeded
from font.hp1345Font import Font
from misc.config import MapConfig, MiscStatsConfig, SignalChartConfig, loadConfig
from misc.mqtt import GnssData, createMqttSubscriber
from palettes.palette import loadPalette
from views.map.generate import getMapSize, prepareInitialMap, readBaseMap
from views.map.update import focusOnPoint, genSatelliteMapGroup
from views.polarGrid.generate import prepareIntialPolarGrid, readBasePolarGrid
from views.polarGrid.update import addSatellitesToPolarGrid
from views.signalGraph.generate import generateBarChart
from views.stats.generate import generateStats

mapConfig = MapConfig()
chartConfig = SignalChartConfig()
mistStatsConfig = MiscStatsConfig()

load_dotenv()
CONFIG = loadConfig()
PALETTE = loadPalette(CONFIG.paletteName)
FONT = Font()

baseMap = readBaseMap()
baseMap, keySize = prepareInitialMap(baseMap, PALETTE, mapConfig)

basePolarGrid = readBasePolarGrid()
basePolarGrid = prepareIntialPolarGrid(basePolarGrid, PALETTE)

# ruff: noqa: PLW0603
LATEST_DATA = None


def updateMap():
	"""Generate and write the latest map"""
	if LATEST_DATA is None:
		return
	satelliteGroup = genSatelliteMapGroup(
		mapConfig, PALETTE, LATEST_DATA.satellites, LATEST_DATA.latitude, LATEST_DATA.longitude
	)
	latestMap = baseMap.replace("<!-- satellites go here -->", satelliteGroup)
	mapSize = getMapSize()
	latestMap = focusOnPoint(latestMap, mapConfig, mapSize, keySize)
	with open("./web/generated/map.svg", "w", encoding="utf-8") as f:
		f.write(latestMap)


def updatePolarGrid():
	"""Generate and write the latest polar grid"""
	if LATEST_DATA is None:
		return
	polarGrid = addSatellitesToPolarGrid(basePolarGrid, PALETTE, LATEST_DATA.satellites)
	with open("./web/generated/polarGrid.svg", "w", encoding="utf-8") as f:
		f.write(polarGrid)


def updateStats():
	"""Generate and write the latest stats"""
	if LATEST_DATA is None:
		return
	(statsSvg, _, _) = generateStats(LATEST_DATA, PALETTE, FONT, mistStatsConfig)
	with open("./web/generated/stats.svg", "w", encoding="utf-8") as f:
		f.write(statsSvg)


def updateChart():
	if LATEST_DATA is None:
		return
	snrChart = generateBarChart(chartConfig, PALETTE, FONT, LATEST_DATA.satellites, 854, 480)
	with open("./web/generated/snrChart.svg", "w", encoding="utf-8") as f:
		f.write(snrChart)


def updateData():
	if LATEST_DATA is None:
		return
	with open("./web/generated/gnssData.json", "w", encoding="utf-8") as f:
		f.write(json.dumps(LATEST_DATA.toJSON(PALETTE)))


def updateSVGsThread():
	"""Update the SVGs in the background once per second"""
	while True:
		startTime = datetime.now()
		updateMap()
		updatePolarGrid()
		updateStats()
		updateChart()
		updateData()
		endTime = datetime.now()

		# sleep for the rest of the second
		timeToSleep = 1 - (endTime - startTime).total_seconds()
		time.sleep(timeToSleep)


def genOnNewDataCallback():
	def onNewData(_: bytes, gnssData: GnssData):
		global LATEST_DATA  # pylint: disable=global-statement
		LATEST_DATA = gnssData

	return onNewData


def main():
	"""Update the generated SVGs/JSON files for the web app"""
	fetchFontRomsIfNeeded()
	createMqttSubscriber(CONFIG.mqtt, CONFIG.satelliteTTL, genOnNewDataCallback())

	if not os.path.exists("./web/generated"):
		os.makedirs("./web/generated")

	with open("./web/generated/palette.json", "w", encoding="utf-8") as f:
		f.write(json.dumps(PALETTE.__dict__))

	thread = threading.Thread(target=updateSVGsThread)
	thread.start()


if __name__ == "__main__":
	main()
