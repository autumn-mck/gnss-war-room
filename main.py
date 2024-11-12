import sys
import json
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtSvgWidgets import QSvgWidget
from palettes.palette import loadPalette
from mapdata.maps import prepareSvg

class MainWindow(QMainWindow):
	def __init__(self, palette, windowConfig):
		super().__init__()

		self.setWindowTitle("GNSS War Room")
		self.setGeometry(100, 100, 700, 500)
		self.setStyleSheet(f"background-color: {palette['background']}; color: {palette['foreground']};")

		svgFile = prepareSvg(palette, windowConfig)
		self.map = QSvgWidget(svgFile, parent=self)
		self.map.setGeometry(0, 0, 700, 500)

		self.show()

app = QApplication(sys.argv)

with open("config.json", "r") as f:
	appConfig = json.load(f)

palette = loadPalette(appConfig["paletteName"])

windows = []
for windowConfig in appConfig["windows"]:
	windows.append(MainWindow(palette, windowConfig))

app.exec()
