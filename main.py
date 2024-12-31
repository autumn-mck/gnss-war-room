#!/usr/bin/env python3

import os
import sys
from typing import Callable
import urllib.request
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from config import loadConfig, MapConfig, PolalGridConfig, MiscStatsConfig, RawMessageConfig
from mqtt import GnssData, createMqttClient
from palettes.palette import loadPalette
from map.window import MapWindow
from polarGrid.window import PolarGridWindow
from stats.window import MiscStatsWindow
from rawMessageWindow import RawMessageWindow

def main():
	"""Main function"""
	fetchHp1345FilesIfNeeded()

	app = QApplication(sys.argv)

	appConfig = loadConfig()

	palette = loadPalette(appConfig.paletteName)
	screens = app.screens()
	windows = []
	count = 0
	for windowConfig in appConfig.windows:
		if isinstance(windowConfig, MapConfig):
			window = MapWindow(palette, windowConfig, count)
		elif isinstance(windowConfig, PolalGridConfig):
			window = PolarGridWindow(palette)
		elif isinstance(windowConfig, MiscStatsConfig):
			window = MiscStatsWindow(palette)
		elif isinstance(windowConfig, RawMessageConfig):
			window = RawMessageWindow(palette)
		else:
			raise ValueError(f"Unknown window type: {windowConfig.type}")
		windows.append(window)
		if appConfig.multiScreen:
			handleMultiScreen(screens, window, count)
		count += 1

	onNewDataCallback = genWindowCallback(windows)
	createMqttClient(appConfig, onNewDataCallback)
	app.exec() # blocks until the app is closed

def handleMultiScreen(screens: list, window: QMainWindow, index: int):
	"""Handle multi-screen setup"""
	screen = screens[index]
	qr = screen.geometry()
	window.move(qr.left(), qr.top())

def genWindowCallback(windows: list[QMainWindow]) -> Callable[[bytes, GnssData], None]:
	"""Generate a callback for the windows to handle new data"""
	lastUpdateTime = datetime.now()
	lastMessageUpdateTime = datetime.now()

	def updateWindowsOnNewData(rawMessage: bytes, gnssData: GnssData):
		nonlocal windows
		nonlocal lastUpdateTime
		nonlocal lastMessageUpdateTime

		# limit how often we update the windows, otherwise pyqt mostly freezes
		timeSinceLastRawMessageUpdate = datetime.now() - lastMessageUpdateTime
		if timeSinceLastRawMessageUpdate < timedelta(seconds=0.01):
			return

		for window in windows:
			if isinstance(window, RawMessageWindow):
				window.onNewData(rawMessage)
		lastMessageUpdateTime = datetime.now()

		timeSinceLastUpdate = datetime.now() - lastUpdateTime
		if timeSinceLastUpdate < timedelta(seconds=0.5):
			return
		lastUpdateTime = datetime.now()

		for window in windows:
			match window:
				case MapWindow():
					window.onNewData(gnssData.satellites, gnssData.latitude, gnssData.longitude)
				case PolarGridWindow():
					window.onNewData(gnssData.satellites)
				case MiscStatsWindow():
					window.onNewData(gnssData)
				case RawMessageWindow():
					# is updated above
					pass
				case _:
					print("Unknown window type")

	return updateWindowsOnNewData

def fetchHp1345FilesIfNeeded():
	"""Download the HP1345A font files if they don't exist"""
	if os.path.isfile("./font/01347-80012.bin"):
		return

	print("Downloading HP1345 font files...")
	charRomUrl = "https://phk.freebsd.dk/_downloads/a89c073235ca9c2b13d657173d32bf78/01347-80012.bin"
	charIndexRomUrl = "https://phk.freebsd.dk/_downloads/2355976608a6359335e30a88e181f1fc/1816-1500.bin"
	firmwareRomUrl = "https://phk.freebsd.dk/_downloads/13f169d8d8dff52497dca435d649f3d0/01347-80010.bin"

	urllib.request.urlretrieve(charRomUrl, "./font/01347-80012.bin")
	urllib.request.urlretrieve(charIndexRomUrl, "./font/1816-1500.bin")
	urllib.request.urlretrieve(firmwareRomUrl, "./font/01347-80010.bin")
	print("Done downloading HP1345 font files")

if __name__ == "__main__":
	main()
