from PyQt6.QtCore import QByteArray, Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QResizeEvent
from PyQt6.QtSvgWidgets import QSvgWidget

from font.hp1345Font import Font
from gnss.nmea import GnssData
from misc.config import SignalChartConfig
from misc.size import Size
from palettes.palette import Palette
from views.baseWindow import BaseWindow
from views.signalGraph.generate import generateBarChart


class SignalGraphWindow(BaseWindow):
	"""Window for displaying signal graph"""

	satelliteReceivedEvent = pyqtSignal()
	textScale = 1.0
	defaultSize = Size(500, 500)

	def __init__(self, palette: Palette, config: SignalChartConfig):
		super().__init__(palette)
		self.setWindowTitle("Signal Graph")
		self.config = config

		self.latestData = GnssData()

		self.sortMethods = ["networkThenPrn", "snr", "elevation"]
		self.sortMethodIndex = 0

		self.svgFont = Font()
		self.svg = QSvgWidget(parent=self)
		self.svg.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))
		self.updateGraph()

		self.satelliteReceivedEvent.connect(self.updateGraph)

		self.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))

	def resizeEvent(self, event: QResizeEvent | None):
		"""Resize the window, and the SNR chart to fit"""
		super().resizeEvent(event)
		if event is None:
			return

		newHeight = event.size().height()
		newWidth = event.size().width()
		self.updateGraph()
		self.svg.setGeometry(0, 0, newWidth, newHeight)

	def keyPressEvent(self, event: QKeyEvent | None):
		"""Handle key presses for the SNR chart window"""
		super().keyPressEvent(event)
		if event is None:
			return

		if event.key() == Qt.Key.Key_S:
			self.sortMethodIndex = (self.sortMethodIndex + 1) % len(self.sortMethods)
			self.updateGraph()
		if event.key() == Qt.Key.Key_U:
			self.config.countUntrackedSatellites = not self.config.countUntrackedSatellites
			self.updateGraph()

	def onNewData(self, gnssData: GnssData):
		self.latestData = gnssData
		self.satelliteReceivedEvent.emit()

	def updateGraph(self):
		"""Update the graph when needed"""
		barChartSvg = generateBarChart(
			self.config,
			self.customPalette,
			self.svgFont,
			self.latestData.satellites,
			self.svg.width(),
			self.svg.height(),
			self.sortMethods[self.sortMethodIndex],
		)
		self.svg.load(QByteArray(barChartSvg.encode()))
