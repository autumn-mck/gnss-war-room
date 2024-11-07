import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtSvgWidgets import QSvgWidget
from palettes.palette import loadPalette
from mapdata.maps import prepareSvg

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		palette = loadPalette("warGames")

		self.setWindowTitle("GNSS War Room")
		self.setGeometry(100, 100, 700, 500)
		self.setStyleSheet(f"background-color: {palette['background']}; color: {palette['foreground']};")

		focusLat = 54.6
		focusLong = -6.0

		svgFile = prepareSvg(palette, {"hideRivers": True, "hideLakes": True, "hideAdmin1Borders": True, "hideAdmin0Borders": False, "focusLat": focusLat, "focusLong": focusLong, "scaleFactor": 4})
		self.map = QSvgWidget(svgFile, parent=self)
		self.map.setGeometry(0, 0, 700, 500)

		self.show()

app = QApplication(sys.argv)
w = MainWindow()
app.exec()