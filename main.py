import sys
import json
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtSvgWidgets import QSvgWidget
from palettes.palette import loadPalette
from mapdata.maps import readBaseSvg, prepareSvg, focusOnPoint, saveTempSvg

class MainWindow(QMainWindow):
	def __init__(self, palette, windowConfig, multiScreen, windowIndex):
		super().__init__()

		defaultWidth = 700
		defaultHeight = 500

		self.palette = palette
		self.windowConfig = windowConfig

		self.setWindowTitle("GNSS War Room")

		self.setGeometry(defaultWidth * windowIndex, 100, defaultWidth, defaultHeight)
		self.setStyleSheet(f"background-color: {palette['background']}; color: {palette['foreground']};")

		svgData = readBaseSvg()
		svgData = prepareSvg(svgData, palette, windowConfig)
		svgData = focusOnPoint(svgData, windowConfig, defaultWidth, defaultHeight)

		self.svgFile = saveTempSvg(svgData)
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, defaultWidth, defaultHeight)

		if multiScreen: self.showFullScreen()
		else: self.show()

	def closeEvent(self, event):
		"""For now, quit app when any window is closed"""
		app.quit()

	def resizeEvent(self, event):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()

		with open(self.svgFile, "r") as f:
			svgData = f.read()

		svgData = focusOnPoint(svgData, self.windowConfig, newX, newY)
		self.svgFile = saveTempSvg(svgData)

		self.map.load(self.svgFile)
		self.map.setGeometry(0, 0, newX, newY)

app = QApplication(sys.argv)

with open("config.json", "r") as f:
	appConfig = json.load(f)

palette = loadPalette(appConfig["paletteName"])

screens = app.screens()
windows = []
count = 0
for windowConfig in appConfig["windows"]:
	window = MainWindow(palette, windowConfig, appConfig["multiScreen"], count)
	windows.append(window)
	if appConfig["multiScreen"]:
		screen = screens[count]
		qr = screen.geometry()
		window.move(qr.left(), qr.top())
	count += 1

app.exec()
