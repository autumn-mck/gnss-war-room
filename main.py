#!/usr/bin/env python3

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from config import loadConfig
from mqtt import createMqttClient
from palettes.palette import loadPalette
from mapdata.maps import MapConfig
from mapWindow import MapWindow
from polarGridWindow import PolarGridWindow

def main():
	"""Main function"""
	app = QApplication(sys.argv)

	appConfig = loadConfig()

	palette = loadPalette(appConfig.paletteName)
	screens = app.screens()
	windows = []
	count = 0
	for windowConfig in appConfig.windows:
		if isinstance(windowConfig, MapConfig):
			window = MapWindow(palette, windowConfig, appConfig.multiScreen, count)
		else:
			window = PolarGridWindow(palette)
		windows.append(window)
		if appConfig.multiScreen:
			handleMultiScreen(screens, window, count)
		count += 1

	createMqttClient(windows, appConfig)
	app.exec() # blocks until the app is closed

def handleMultiScreen(screens: list, window: QMainWindow, index: int):
	"""Handle multi-screen setup"""
	screen = screens[index]
	qr = screen.geometry()
	window.move(qr.left(), qr.top())

if __name__ == "__main__":
	main()
