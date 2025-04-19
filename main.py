#!/usr/bin/env python3

import contextlib
import signal
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
	WindowConfig,
	loadConfig,
)
from misc.mqtt import createMqttSubscriber
from palettes.palette import Palette, loadPalette
from views.baseWindow import BaseWindow
from views.globe.window import GlobeWindow
from views.map.window import MapWindow
from views.polarGrid.window import PolarGridWindow
from views.rawMessages.window import RawMessageWindow
from views.signalGraph.window import SignalGraphWindow
from views.startup.window import StartupWindow
from views.stats.window import MiscStatsWindow


def main():
	"""Desktop UI main function"""
	signal.signal(signal.SIGINT, exitCleanlyOnInterrupt)

	fetchFontRomsIfNeeded()

	load_dotenv()
	config = loadConfig()
	palette = loadPalette(config.paletteName)

	app = QApplication(sys.argv)
	if config.startupSequence:
		windows = startupSequenceThenMainWindows(app, config, palette)
	else:
		windows = createMainWindows(config, palette)

	if config.warRoom:
		fullscreenWindowsOnAllDisplays(app, windows)
	else:
		showAllWindows(windows)

	app.exec()  # blocks until the app is closed
	print("How about a nice game of chess?")


def exitCleanlyOnInterrupt(signalId: int, _):
	"""Exit the program on a KeyboardInterrupt"""
	print(f"{signalId} KeyboardInterrupt: Exiting...")
	sys.exit(0)


def startupSequenceThenMainWindows(app: QApplication, config: Config, palette: Palette):
	"""Display the optional startup sequence, then return the main windows"""
	screens = app.screens()
	windows = []
	for index, screen in enumerate(screens):
		window = StartupWindow(palette, app) if index == 0 else BaseWindow(palette)

		fullscreenWindowOnDisplay(window, screen)
		windows.append(window)

	windows = createMainWindows(config, palette)
	# if anything goes wrong, just continue to the main visualisation anyway
	with contextlib.suppress(Exception):
		app.exec()

	return windows


def fullscreenWindowOnDisplay(window: QMainWindow, display: QScreen):
	displayGeometry = display.geometry()
	window.setScreen(display)
	window.move(displayGeometry.topLeft())
	window.resize(displayGeometry.size())
	window.showFullScreen()


def createMainWindows(config: Config, palette: Palette):
	"""Create the main windows"""
	windows = [windowConfigToWindow(windowConfig, palette) for windowConfig in config.windows]

	onNewData = updateWindows(windows)
	threading.Thread(
		target=createMqttSubscriber, args=(config.mqtt, config.satelliteTTL, onNewData)
	).start()
	return windows


def fullscreenWindowsOnAllDisplays(app: QApplication, windows: list[BaseWindow]):
	"""Make all the windows fullscreen on all available screens"""
	displays = app.screens()
	for index, window in enumerate(windows):
		display = displays[index % len(displays)]
		fullscreenWindowOnDisplay(window, display)


def showAllWindows(windows: list[BaseWindow]):
	for window in windows:
		window.show()


def windowConfigToWindow(windowConfig: WindowConfig, palette: Palette) -> BaseWindow:
	"""Map the window config to a window and return it"""
	match windowConfig:
		case MapConfig():
			return MapWindow(palette, windowConfig)
		case PolalGridConfig():
			return PolarGridWindow(palette)
		case MiscStatsConfig():
			return MiscStatsWindow(palette, windowConfig)
		case RawMessageConfig():
			return RawMessageWindow(palette, windowConfig)
		case SignalChartConfig():
			return SignalGraphWindow(palette, windowConfig)
		case GlobeConfig():
			return GlobeWindow(palette, windowConfig)
		case _:
			msg = f"Unknown window type: {windowConfig.type}"
			raise ValueError(msg)


def updateWindows(windows: list[BaseWindow]) -> Callable[[bytes, GnssData], None]:
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
			updateWindow(window, gnssData)

	return updateWindowsOnNewData


def updateWindow(window: BaseWindow, gnssData: GnssData):
	"""Update the given window with the given data"""
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
		case GlobeWindow():
			pass  # is managed by whatever server the globe is on
		case _:
			msg = f"Unknown window type: {window}"
			raise ValueError(msg)


if __name__ == "__main__":
	main()
