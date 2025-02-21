#!/usr/bin/env python3

import sys
from datetime import datetime, timedelta
from typing import Callable

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow

from font.fetch import fetchFontRomsIfNeeded
from gnss.nmea import GnssData
from misc.config import (
	Config,
	GlobeConfig,
	MapConfig,
	MiscStatsConfig,
	PolalGridConfig,
	RawMessageConfig,
	SignalChartConfig,
	loadConfig,
)
from misc.mqtt import createMqttSubscriber
from palettes.palette import Palette, loadPalette
from views.map.window import MapWindow
from views.polarGrid.window import PolarGridWindow
from views.rawMessages.window import RawMessageWindow
from views.signalGraph.window import SignalGraphWindow
from views.stats.window import MiscStatsWindow


def main():
	"""Main function"""
	fetchFontRomsIfNeeded()

	app = QApplication(sys.argv)
	config = loadConfig()
	palette = loadPalette(config.paletteName)
	windows = createWindows(config, palette)

	if config.warRoom:
		fullscreenWindowsOnAllScreens(app, windows)

	onNewData = updateWindows(windows)
	createMqttSubscriber(config.mqtt, config.satelliteTTL, onNewData)
	app.exec()  # blocks until the app is closed


def fullscreenWindowsOnAllScreens(app: QApplication, windows: list[QMainWindow]):
	"""Make all the windows fullscreen on all available screens"""
	screens = app.screens()
	for index, window in enumerate(windows):
		screen = screens[index % len(screens)]
		screenGeometry = screen.geometry()
		window.setScreen(screen)
		window.move(screenGeometry.topLeft())
		window.resize(screenGeometry.size())
		window.showFullScreen()


def createWindows(appConfig: Config, palette: Palette):
	"""Create the windows from the given config"""
	windows: list[QMainWindow] = []
	for windowConfig in appConfig.windows:
		match windowConfig:
			case MapConfig():
				window = MapWindow(palette, windowConfig)
			case PolalGridConfig():
				window = PolarGridWindow(palette)
			case MiscStatsConfig():
				window = MiscStatsWindow(palette, windowConfig)
			case RawMessageConfig():
				window = RawMessageWindow(palette, windowConfig)
			case SignalChartConfig():
				window = SignalGraphWindow(palette, windowConfig)
			case GlobeConfig():
				window = QWebEngineView()
				window.load(QUrl("http://0.0.0.0:2024/"))
				window.show()
			case _:
				msg = f"Unknown window type: {windowConfig.type}"
				raise ValueError(msg)

		windows.append(window)
	return windows


def updateWindows(windows: list[QMainWindow]) -> Callable[[bytes, GnssData], None]:
	"""Generate a callback for the windows to handle new data"""
	lastUpdatedAt = datetime.now()

	def updateWindowsOnNewData(rawMessage: bytes, gnssData: GnssData):
		nonlocal windows
		nonlocal lastUpdatedAt

		for window in windows:
			if isinstance(window, RawMessageWindow):
				window.onNewData(rawMessage)

		# limit how often we update the windows, otherwise pyqt mostly freezes
		timeSinceLastUpdate = datetime.now() - lastUpdatedAt
		if timeSinceLastUpdate < timedelta(seconds=0.5):
			return
		lastUpdatedAt = datetime.now()

		for window in windows:
			match window:
				case MapWindow():
					window.onNewData(gnssData.satellites, gnssData.latitude, gnssData.longitude)
				case PolarGridWindow():
					window.onNewData(gnssData.satellites)
				case MiscStatsWindow():
					window.onNewData(gnssData)
				case RawMessageWindow():
					window.satelliteReceivedEvent.emit()
				case SignalGraphWindow():
					window.onNewData(gnssData)
				case _:
					print("Unknown window type")

	return updateWindowsOnNewData


if __name__ == "__main__":
	main()
