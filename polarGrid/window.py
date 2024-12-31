from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtCore import pyqtSignal
from palettes.palette import Palette
from misc import saveToTempFile
from gnss.satellite import SatelliteInView
from polarGrid.generate import readBasePolarGrid, prepareIntialPolarGrid
from polarGrid.update import addSatellitesToPolarGrid

class PolarGridWindow(QMainWindow):
	"""Window for displaying the positions of satellites"""
	satelliteReceivedEvent = pyqtSignal()

	def __init__(self, palette: Palette):
		super().__init__()

		self.customPalette = palette
		self.latestSatellites = []

		self.svgFile = self.generateNewGrid()
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, 400, 400)

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.setWindowTitle("Polar Grid")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.show()

	def generateNewGrid(self):
		svgData = readBasePolarGrid()
		svgData = prepareIntialPolarGrid(svgData, self.customPalette)
		self.basePolarGrid = svgData
		return saveToTempFile(svgData)

	def updateGrid(self):
		svgData = addSatellitesToPolarGrid(self.basePolarGrid, self.customPalette, self.latestSatellites)
		return saveToTempFile(svgData)

	def resizeEvent(self, event: QResizeEvent):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()
		minSize = min(newX, newY)
		self.map.setGeometry(0, 0, minSize, minSize)

	def onNewData(self, satellites: list[SatelliteInView]):
		self.latestSatellites = satellites
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		self.svgFile = self.updateGrid()
		self.map.load(self.svgFile)
