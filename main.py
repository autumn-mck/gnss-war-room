import sys
from dataclasses import dataclass
from dataclass_wizard import JSONWizard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from palettes.palette import loadPalette
from mapdata.maps import MapConfig, PolalGridConfig
from mapWindow import MapWindow
from polarGridWindow import PolarGridWindow

@dataclass
class Config(JSONWizard):
	"""Configuration for the app"""
	class _(JSONWizard.Meta):
		tag_key = "type"

	paletteName: str
	multiScreen: bool
	windows: list[MapConfig | PolalGridConfig]

def main():
	"""Main function"""
	app = QApplication(sys.argv)

	with open("config.json", "r", encoding="utf8") as f:
		appConfig = Config.from_json(f.read())
		if isinstance(appConfig, list):
			appConfig = appConfig[0]

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

	app.exec()

def handleMultiScreen(screens: list, window: QMainWindow, index: int):
	"""Handle multi-screen setup"""
	screen = screens[index]
	qr = screen.geometry()
	window.move(qr.left(), qr.top())

if __name__ == "__main__":
	main()
