import sys
from dataclasses import dataclass
from dataclass_wizard import JSONWizard
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtSvgWidgets import QSvgWidget
from palettes.palette import loadPalette, Palette
from mapdata.maps import readBaseSvg, prepareSvg, focusOnPoint, saveToTempFile, MapConfig

@dataclass
class Config(JSONWizard):
	paletteName: str
	multiScreen: bool
	windows: list[MapConfig]

class MapWindow(QMainWindow):
	"""Configurable map window"""
	def __init__(self, palette: Palette, windowConfig: MapConfig, multiScreen: bool, windowIndex: int):
		super().__init__()

		defaultWidth = 700
		defaultHeight = 500

		self.windowConfig = windowConfig

		self.setWindowTitle("GNSS War Room")

		self.setGeometry(defaultWidth * windowIndex, 100, defaultWidth, defaultHeight)
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

		mapSvg = readBaseSvg()
		mapSvg = prepareSvg(mapSvg, palette, windowConfig)
		mapSvg = focusOnPoint(mapSvg, windowConfig, defaultWidth, defaultHeight)

		self.svgFile = saveToTempFile(mapSvg)
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, defaultWidth, defaultHeight)

		if multiScreen:
			self.showFullScreen()
		else:
			self.show()

	def resizeEvent(self, event):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()

		with open(self.svgFile, "r", encoding="utf8") as f:
			mapSvg = f.read()

		mapSvg = focusOnPoint(mapSvg, self.windowConfig, newX, newY)
		self.svgFile = saveToTempFile(mapSvg)

		self.map.load(self.svgFile)
		self.map.setGeometry(0, 0, newX, newY)


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
