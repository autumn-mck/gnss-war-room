#!/usr/bin/env python3

import contextlib
import sys
import threading
from datetime import datetime, timedelta
from typing import Callable

from dotenv import load_dotenv
from PyQt6.QtGui import QScreen
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
from views.globe.window import GlobeWindow
from views.map.window import MapWindow
from views.polarGrid.window import PolarGridWindow
from views.rawMessages.window import RawMessageWindow
from views.signalGraph.window import SignalGraphWindow
from views.startup.blankWindow import BlankWindow
from views.startup.window import StartupWindow
from views.stats.window import MiscStatsWindow


def main():
	"""Main function"""
	fetchFontRomsIfNeeded()

	app = QApplication(sys.argv)
	load_dotenv()
	config = loadConfig()
	palette = loadPalette(config.paletteName)
	if config.startupSequence:
		windows = startupSequence(app, config, palette)
	else:
		windows = createMainWindows(config, palette)

	if config.warRoom:
		fullscreenWindowsOnAllScreens(app, windows)
	else:
		for window in windows:
			window.show()

	app.exec()  # blocks until the app is closed
	print("How about a nice game of chess?")


def startupSequence(app: QApplication, config: Config, palette: Palette):
	"""Display the startup sequence, then return the main windows"""
	screens = app.screens()
	windows = []
	for index, screen in enumerate(screens):
		window = StartupWindow(palette, app) if index == 0 else BlankWindow(palette)

		fullscreenWindowOnScreen(window, screen)
		windows.append(window)

	windows = createMainWindows(config, palette)
	with contextlib.suppress(Exception):
		app.exec()

	return windows


def fullscreenWindowOnScreen(window: QMainWindow, screen: QScreen):
	screenGeometry = screen.geometry()
	window.setScreen(screen)
	window.move(screenGeometry.topLeft())
	window.resize(screenGeometry.size())
	window.showFullScreen()


def createMainWindows(config: Config, palette: Palette):
	"""Create the main windows"""
	windows = createWindows(config, palette)

	onNewData = updateWindows(windows)
	threading.Thread(
		target=createMqttSubscriber, args=(config.mqtt, config.satelliteTTL, onNewData)
	).start()
	return windows


def fullscreenWindowsOnAllScreens(app: QApplication, windows: list[QMainWindow]):
	"""Make all the windows fullscreen on all available screens"""
	screens = app.screens()
	for index, window in enumerate(windows):
		screen = screens[index % len(screens)]
		fullscreenWindowOnScreen(window, screen)


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
				window = GlobeWindow(palette, windowConfig)
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
					window.onNewData(gnssData)
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
