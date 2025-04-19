from PyQt6.QtCore import QByteArray, pyqtSignal
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtSvgWidgets import QSvgWidget

from gnss.satellite import SatelliteInView
from misc.size import Size
from palettes.palette import Palette
from views.baseWindow import BaseWindow
from views.polarGrid.generate import prepareIntialPolarGrid, readBasePolarGrid
from views.polarGrid.update import addSatellitesToPolarGrid


class PolarGridWindow(BaseWindow):
	"""Window for displaying the positions of satellites"""

	satelliteReceivedEvent = pyqtSignal()

	def __init__(self, palette: Palette):
		super().__init__(palette)

		self.latestSatellites = []

		self.svgFile = self.generateNewGrid()
		self.polarGrid = QSvgWidget(parent=self)
		self.polarGrid.load(self.svgFile)
		self.polarGrid.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.setWindowTitle("Polar Grid")

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

	def onNewData(self, satellites: list[SatelliteInView]):
		self.latestSatellites = satellites
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		self.svgFile = self.updateGrid()
		self.polarGrid.load(self.svgFile)
