import time
import threading

from config import loadConfig, MapConfig
from mqtt import GnssData, createMqttClient
from palettes.palette import loadPalette
from map.generate import readBaseSvg, prepareInitialSvg
from map.update import genSatelliteGroup

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

config = loadConfig()
palette = loadPalette("warGames")

baseSvg = readBaseSvg()
baseSvg = prepareInitialSvg(baseSvg, palette, mapConfig)

latestSvg = baseSvg
latestData = None

def updateMap():
	global baseSvg
	global latestData
	global palette
	global mapConfig
	global latestSvg
	if latestData is None:
		return
	satelliteGroup = genSatelliteGroup(
		mapConfig,
		palette,
		latestData.satellites,
		latestData.latitude,
		latestData.longitude
	)
	latestSvg = baseSvg.replace('</svg>', satelliteGroup + '\n</svg>')
	with open('./web/map.svg', 'w', encoding='utf-8') as f:
		f.write(latestSvg)

def updateMapThread():
	while True:
		updateMap()
		time.sleep(1)

def genOnNewDataCallback():
	def onNewData(_: bytes, gnssData: GnssData):
		global latestData
		latestData = gnssData
	return onNewData

def main():

	createMqttClient(config, genOnNewDataCallback())

	thread = threading.Thread(target=updateMapThread)
	thread.start()

if __name__ == '__main__':
	main()