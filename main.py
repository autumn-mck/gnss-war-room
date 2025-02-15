#!/usr/bin/env python3

import sys
from typing import Callable
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pynmeagps import NMEAReader, NMEAMessage

from misc.config import (
	SignalChartConfig,
	loadConfig,
	MapConfig,
	PolalGridConfig,
	MiscStatsConfig,
	RawMessageConfig,
	GlobeConfig,
)
from misc.mqtt import createMqttSubscriberClient
from gnss.nmea import GnssData
from palettes.palette import loadPalette
from views.map.window import MapWindow
from views.polarGrid.window import PolarGridWindow
from views.stats.window import MiscStatsWindow
from views.rawMessages.window import RawMessageWindow
from views.signalGraph.window import SignalGraphWindow
from font.fetch import fetchHp1345FilesIfNeeded


def main():
	"""Main function"""
	fetchHp1345FilesIfNeeded()

	app = QApplication(sys.argv)

	appConfig = loadConfig()

	palette = loadPalette(appConfig.paletteName)
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
		elif isinstance(windowConfig, GlobeConfig):
			window = QWebEngineView()
			window.load(QUrl("http://0.0.0.0:2024/"))
			window.show()
		else:
			raise ValueError(f"Unknown window type: {windowConfig.type}")
		windows.append(window)
		# if appConfig.multiScreen:
		# 	handleMultiScreen(screens, window, count)
		count += 1

	onNewDataCallback = genWindowCallback(windows)
	createMqttSubscriberClient(appConfig, onNewDataCallback)
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
	lastFinalMessageUpdateTime = datetime.now()

	def updateWindowsOnNewData(rawMessage: bytes, gnssData: GnssData):
		nonlocal windows
		nonlocal lastUpdateTime
		nonlocal lastMessageUpdateTime
		nonlocal lastFinalMessageUpdateTime

		firstWithTimeMessageID = "RMC"
		timeSinceLastFinalMessageUpdate = datetime.now() - lastFinalMessageUpdateTime
		msg = NMEAReader.parse(rawMessage)
		shouldForceUpdate = (
			isinstance(msg, NMEAMessage)
			and msg.msgID == firstWithTimeMessageID
			and timeSinceLastFinalMessageUpdate > timedelta(seconds=0.5)
		)
		if shouldForceUpdate:
			lastFinalMessageUpdateTime = datetime.now()

		# limit how often we update the windows, otherwise pyqt mostly freezes
		timeSinceLastRawMessageUpdate = datetime.now() - lastMessageUpdateTime
		if timeSinceLastRawMessageUpdate < timedelta(seconds=0.05) and not shouldForceUpdate:
			return

		for window in windows:
			if isinstance(window, RawMessageWindow):
				window.onNewData(rawMessage)
		lastMessageUpdateTime = datetime.now()

		timeSinceLastUpdate = datetime.now() - lastUpdateTime
		if timeSinceLastUpdate < timedelta(seconds=0.2) and not shouldForceUpdate:
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
