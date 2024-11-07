import sys
import json
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtSvgWidgets import QSvgWidget
from palettes.palette import loadPalette
from mapdata.maps import prepareSvg

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		with open("config.json", "r") as f:
			config = json.load(f)

		palette = loadPalette(config["paletteName"])

		self.setWindowTitle("GNSS War Room")
		self.setGeometry(100, 100, 700, 500)
		self.setStyleSheet(f"background-color: {palette['background']}; color: {palette['foreground']};")

		svgFile = prepareSvg(palette, config["mapConfig"])
		self.map = QSvgWidget(svgFile, parent=self)
		self.map.setGeometry(0, 0, 700, 500)

		self.show()

app = QApplication(sys.argv)
w = MainWindow()
app.exec()