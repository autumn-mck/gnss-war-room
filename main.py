#!/usr/bin/env python3

import sys
from typing import Callable
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from config import (
	SignalChartConfig,
	loadConfig,
	MapConfig,
	PolalGridConfig,
	MiscStatsConfig,
	RawMessageConfig,
)
from gnss.nmea import GnssData
from mqtt import createMqttClient
from palettes.palette import loadPalette
from map.window import MapWindow
from polarGrid.window import PolarGridWindow
from stats.window import MiscStatsWindow
from rawMessages.window import RawMessageWindow
from misc import fetchHp1345FilesIfNeeded
from signalGraph.window import SignalGraphWindow


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
			window = MapWindow(palette, windowConfig)
		elif isinstance(windowConfig, PolalGridConfig):
			window = PolarGridWindow(palette)
		elif isinstance(windowConfig, MiscStatsConfig):
			window = MiscStatsWindow(palette, windowConfig)
		elif isinstance(windowConfig, RawMessageConfig):
			window = RawMessageWindow(palette, windowConfig)
		elif isinstance(windowConfig, SignalChartConfig):
			window = SignalGraphWindow(palette, windowConfig)
		else:
			raise ValueError(f"Unknown window type: {windowConfig.type}")
		windows.append(window)
		if appConfig.multiScreen:
			handleMultiScreen(screens, window, count)
		count += 1

	onNewDataCallback = genWindowCallback(windows)
	createMqttClient(appConfig, onNewDataCallback)
	app.exec()  # blocks until the app is closed


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
				case SignalGraphWindow():
					window.onNewData(gnssData)
				case _:
					print("Unknown window type")

	return updateWindowsOnNewData


if __name__ == "__main__":
	main()
