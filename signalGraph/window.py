from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import pyqtSignal, QByteArray
from PyQt6.QtGui import QResizeEvent
from config import SignalChartConfig
from font.hp1345Font import Font
from gnss.nmea import GnssData
from palettes.palette import Palette
from signalGraph.generate import generateBarChart


class SignalGraphWindow(QMainWindow):
	"""Window for displaying signal graph"""

	satelliteReceivedEvent = pyqtSignal()
	textScale = 1.0

	def __init__(self, palette: Palette, config: SignalChartConfig):
		super().__init__()
		self.setWindowTitle("Signal Graph")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette
		self.config = config

		self.latestData = GnssData()

		self.svgFont = Font()
		self.svg = QSvgWidget(parent=self)
		self.svg.setGeometry(0, 0, 500, 500)
		self.updateGraph()

		self.satelliteReceivedEvent.connect(self.updateGraph)

		self.setGeometry(0, 0, 500, 500)
		self.show()

	def resizeEvent(self, event: QResizeEvent):
		newWidth = event.size().width()
		newHeight = event.size().height()
		self.updateGraph()
		self.svg.setGeometry(0, 0, newWidth, newHeight)

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
		)
		self.svg.load(QByteArray(barChartSvg.encode()))
