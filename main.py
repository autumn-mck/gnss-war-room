import sys
from dataclasses import dataclass
from dataclass_wizard import JSONWizard
from PyQt6.QtWidgets import QApplication
from palettes.palette import loadPalette
from mapdata.maps import MapConfig
from mapWindow import MapWindow

@dataclass
class Config(JSONWizard):
	paletteName: str
	multiScreen: bool
	windows: list[MapConfig]

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
		window = MapWindow(palette, windowConfig, appConfig.multiScreen, count)
		windows.append(window)
		if appConfig.multiScreen:
			handleMultiScreen(screens, window, count)
		count += 1

	app.exec()

def handleMultiScreen(screens: list, window: MapWindow, index: int):
	"""Handle multi-screen setup"""
	screen = screens[index]
	qr = screen.geometry()
	window.move(qr.left(), qr.top())

if __name__ == "__main__":
	main()
