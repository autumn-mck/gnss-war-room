import sys
import json
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QScreen
from PyQt6.QtSvgWidgets import QSvgWidget
from palettes.palette import loadPalette
from mapdata.maps import prepareSvg

class MainWindow(QMainWindow):
	def __init__(self, palette, windowConfig, multiScreen):
		super().__init__()

		self.setWindowTitle("GNSS War Room")
		self.setGeometry(100, 100, 700, 500)
		self.setStyleSheet(f"background-color: {palette['background']}; color: {palette['foreground']};")

		svgFile = prepareSvg(palette, windowConfig)
		self.map = QSvgWidget(svgFile, parent=self)
		self.map.setGeometry(0, 0, 700, 500)

		if multiScreen: self.showFullScreen()
		else: self.show()

app = QApplication(sys.argv)

with open("config.json", "r") as f:
	appConfig = json.load(f)

palette = loadPalette(appConfig["paletteName"])

multiScreen = False
screens = app.screens()
windows = []
count = 0
for windowConfig in appConfig["windows"]:
	window = MainWindow(palette, windowConfig, multiScreen)
	windows.append(window)
	if multiScreen:
		screen = screens[count]
		qr = screen.geometry()
		window.move(qr.left(), qr.top())
	count += 1

app.exec()
