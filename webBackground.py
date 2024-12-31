from datetime import datetime
import time
import threading

from config import loadConfig, MapConfig
from font.hp1345Font import Font
from mqtt import GnssData, createMqttClient
from palettes.palette import loadPalette
from map.generate import readBaseMap, prepareInitialMap
from map.update import genSatelliteMapGroup
from polarGrid.generate import readBasePolarGrid, prepareIntialPolarGrid
from polarGrid.update import addSatellitesToPolarGrid
from stats.generate import generateStats

mapConfig = MapConfig(
    scaleFactor=2,
    scaleMethod="fit",
    focusLat=0,
    focusLong=10,
    hideCities=True,
    hideAdmin0Borders=False,
    hideAdmin1Borders=True,
    hideRivers=True,
    hideLakes=True
)

CONFIG = loadConfig()
PALETTE = loadPalette("warGames")
FONT = Font()

baseMap = readBaseMap()
baseMap = prepareInitialMap(baseMap, PALETTE, mapConfig)

basePolarGrid = readBasePolarGrid()
basePolarGrid = prepareIntialPolarGrid(basePolarGrid, PALETTE)

LATEST_DATA = None

def updateMap():
	"""Generate and write the latest map"""
	if LATEST_DATA is None:
		return
	satelliteGroup = genSatelliteMapGroup(mapConfig, PALETTE,
		LATEST_DATA.satellites,
		LATEST_DATA.latitude,
		LATEST_DATA.longitude
	)
	latestMap = baseMap.replace('</svg>', satelliteGroup + '\n</svg>')
	with open('./web/map.svg', 'w', encoding='utf-8') as f:
		f.write(latestMap)

def updatePolarGrid():
	"""Generate and write the latest polar grid"""
	if LATEST_DATA is None:
		return
	polarGrid = addSatellitesToPolarGrid(basePolarGrid, PALETTE, LATEST_DATA.satellites)
	with open('./web/polarGrid.svg', 'w', encoding='utf-8') as f:
		f.write(polarGrid)

def updateStats():
	"""Generate and write the latest stats"""
	if LATEST_DATA is None:
		return
	statsSvg, _, _ = generateStats(LATEST_DATA, PALETTE, FONT)
	with open('./web/stats.svg', 'w', encoding='utf-8') as f:
		f.write(statsSvg)

def updateSVGsThread():
	"""Update the SVGs in the background once per second"""
	while True:
		startTime = datetime.now()
		updateMap()
		updatePolarGrid()
		updateStats()
		endTime = datetime.now()

		# sleep for the rest of the second
		timeToSleep = 1 - (endTime - startTime).total_seconds()
		time.sleep(timeToSleep)

def genOnNewDataCallback():
	def onNewData(_: bytes, gnssData: GnssData):
		global LATEST_DATA # pylint: disable=global-statement
		LATEST_DATA = gnssData
	return onNewData

def main():
	createMqttClient(CONFIG, genOnNewDataCallback())

	thread = threading.Thread(target=updateSVGsThread)
	thread.start()

if __name__ == '__main__':
	main()
