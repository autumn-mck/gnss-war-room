from datetime import datetime
import json
import time
import threading

from misc.mqtt import GnssData, createMqttSubscriberClient
from misc.config import MiscStatsConfig, loadConfig, MapConfig, SignalChartConfig
from font.hp1345Font import Font
from font.fetch import fetchHp1345FilesIfNeeded
from palettes.palette import loadPalette
from views.map.generate import readBaseMap, prepareInitialMap, getMapSize
from views.map.update import genSatelliteMapGroup, focusOnPoint
from views.polarGrid.generate import readBasePolarGrid, prepareIntialPolarGrid
from views.polarGrid.update import addSatellitesToPolarGrid
from views.stats.generate import generateStats
from views.signalGraph.generate import generateBarChart

mapConfig = MapConfig()
chartConfig = SignalChartConfig()
mistStatsConfig = MiscStatsConfig()

CONFIG = loadConfig()
PALETTE = loadPalette("warGames")
FONT = Font()

baseMap = readBaseMap()
baseMap, keySize = prepareInitialMap(baseMap, PALETTE, mapConfig)

basePolarGrid = readBasePolarGrid()
basePolarGrid = prepareIntialPolarGrid(basePolarGrid, PALETTE)

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
	with open("./web/map.svg", "w", encoding="utf-8") as f:
		f.write(latestMap)


def updatePolarGrid():
	"""Generate and write the latest polar grid"""
	if LATEST_DATA is None:
		return
	polarGrid = addSatellitesToPolarGrid(basePolarGrid, PALETTE, LATEST_DATA.satellites)
	with open("./web/polarGrid.svg", "w", encoding="utf-8") as f:
		f.write(polarGrid)


def updateStats():
	"""Generate and write the latest stats"""
	if LATEST_DATA is None:
		return
	(statsSvg, _, _) = generateStats(LATEST_DATA, PALETTE, FONT, mistStatsConfig)
	with open("./web/stats.svg", "w", encoding="utf-8") as f:
		f.write(statsSvg)


def updateChart():
	if LATEST_DATA is None:
		return
	snrChart = generateBarChart(chartConfig, PALETTE, FONT, LATEST_DATA.satellites, 854, 480)
	with open("./web/snrChart.svg", "w", encoding="utf-8") as f:
		f.write(snrChart)


def updateData():
	if LATEST_DATA is None:
		return
	with open("./web/gnssData.json", "w", encoding="utf-8") as f:
		f.write(json.dumps(LATEST_DATA.toJSON()))


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
	fetchHp1345FilesIfNeeded()
	createMqttSubscriberClient(CONFIG, genOnNewDataCallback())

	thread = threading.Thread(target=updateSVGsThread)
	thread.start()


if __name__ == "__main__":
	main()
