from PyQt6.QtCore import QByteArray, Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QResizeEvent
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QMainWindow

from gnss.satellite import SatelliteInView
from misc.size import Size
from palettes.palette import Palette
from views.polarGrid.generate import prepareIntialPolarGrid, readBasePolarGrid
from views.polarGrid.update import addSatellitesToPolarGrid


class PolarGridWindow(QMainWindow):
	"""Window for displaying the positions of satellites"""

	satelliteReceivedEvent = pyqtSignal()
	defaultSize = Size(500, 500)

	def __init__(self, palette: Palette):
		super().__init__()

		self.customPalette = palette
		self.latestSatellites = []

		self.svgFile = self.generateNewGrid()
		self.polarGrid = QSvgWidget(parent=self)
		self.polarGrid.load(self.svgFile)
		self.polarGrid.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))
		self.setWindowTitle("Polar Grid")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

	def generateNewGrid(self):
		svgData = readBasePolarGrid()
		svgData = prepareIntialPolarGrid(svgData, self.customPalette)
		self.basePolarGrid = svgData
		return QByteArray(svgData.encode())

	def updateGrid(self):
		svgData = addSatellitesToPolarGrid(
			self.basePolarGrid, self.customPalette, self.latestSatellites
		)
		return QByteArray(svgData.encode())

	def resizeEvent(self, event: QResizeEvent):
		newX = event.size().width()
		newY = event.size().height()
		minSize = min(newX, newY)
		self.polarGrid.setGeometry(
			int((newX - minSize) / 2), int((newY - minSize) / 2), minSize, minSize
		)

	def keyPressEvent(self, event: QKeyEvent):
		if event.key() == Qt.Key.Key_F:
			self.setWindowState(self.windowState() ^ Qt.WindowState.WindowFullScreen)

	def onNewData(self, satellites: list[SatelliteInView]):
		self.latestSatellites = satellites
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		self.svgFile = self.updateGrid()
		self.polarGrid.load(self.svgFile)
