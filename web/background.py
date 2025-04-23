import json
import os
import statistics
import threading
import time
from datetime import datetime

from dotenv import load_dotenv

from font.fetch import fetchFontRomsIfNeeded
from font.hp1345Font import Font
from gnss.nmea import ADSBData
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
GNSS_DATA = GnssData()
ADSB_DATA = ADSBData()


def updateMap():
	"""Generate and write the latest map"""
	satelliteGroup = genSatelliteMapGroup(
		mapConfig,
		PALETTE,
		GNSS_DATA.satellites,
		ADSB_DATA.flights,
		GNSS_DATA.latitude,
		GNSS_DATA.longitude,
		GNSS_DATA.date,
	)
	latestMap = baseMap.replace("<!-- satellites go here -->", satelliteGroup)
	mapSize = getMapSize()
	latestMap = focusOnPoint(latestMap, mapConfig, mapSize, keySize)
	with open("./web/generated/map.svg", "w", encoding="utf-8") as f:
		f.write(latestMap)


def updatePolarGrid():
	polarGrid = addSatellitesToPolarGrid(basePolarGrid, PALETTE, GNSS_DATA.satellites)
	with open("./web/generated/polarGrid.svg", "w", encoding="utf-8") as f:
		f.write(polarGrid)


def updateStats():
	(statsSvg, _, _) = generateStats(GNSS_DATA, PALETTE, FONT, mistStatsConfig)
	with open("./web/generated/stats.svg", "w", encoding="utf-8") as f:
		f.write(statsSvg)


def updateChart():
	snrChart = generateBarChart(chartConfig, PALETTE, FONT, GNSS_DATA.satellites, 854, 480)
	with open("./web/generated/snrChart.svg", "w", encoding="utf-8") as f:
		f.write(snrChart)


def updateData():
	with open("./web/generated/gnssData.json", "w", encoding="utf-8") as f:
		f.write(json.dumps(GNSS_DATA.toJSON(PALETTE)))


def updateWoprData():
	"""Generate and write data for the WOPR endpoint"""
	woprData = {
		"latitude": GNSS_DATA.latitude,
		"longitude": GNSS_DATA.longitude,
		"altitude": GNSS_DATA.altitude,
		"pdop": GNSS_DATA.pdop,
		"avgSnr": statistics.mean([satellite.snr for satellite in GNSS_DATA.satellites]),
	}

	with open("./web/generated/wopr.json", "w", encoding="utf-8") as f:
		f.write(json.dumps(woprData))


def updateSVGsThread():
	"""Update the SVGs in the background once per second"""
	while True:
		startTime = datetime.now()
		updateMap()
		updatePolarGrid()
		updateStats()
		updateChart()
		updateData()
		updateWoprData()
		endTime = datetime.now()

		# sleep for the rest of the second
		timeToSleep = 1 - (endTime - startTime).total_seconds()
		time.sleep(timeToSleep)


def genOnNewDataCallback():
	"""Generate a function to update the global GNSS and ADS-B data"""

	def onNewData(_: bytes, gnssData: GnssData, adsbData: ADSBData):
		global GNSS_DATA  # pylint: disable=global-statement
		global ADSB_DATA  # pylint: disable=global-statement
		ADSB_DATA = adsbData
		GNSS_DATA = gnssData

	return onNewData


def main():
	"""Update the generated SVGs/JSON files for the web app"""
	fetchFontRomsIfNeeded()
	createMqttSubscriber(CONFIG, genOnNewDataCallback())

	if not os.path.exists("./web/generated"):
		os.makedirs("./web/generated")

	with open("./web/generated/palette.json", "w", encoding="utf-8") as f:
		f.write(json.dumps(PALETTE.__dict__))

	thread = threading.Thread(target=updateSVGsThread)
	thread.start()


if __name__ == "__main__":
	main()
