from PyQt6.QtCore import QByteArray, Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QResizeEvent
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QMainWindow

from font.hp1345Font import Font
from gnss.nmea import GnssData
from misc.config import SignalChartConfig
from misc.size import Size
from palettes.palette import Palette
from views.signalGraph.generate import generateBarChart


class SignalGraphWindow(QMainWindow):
	"""Window for displaying signal graph"""

	satelliteReceivedEvent = pyqtSignal()
	textScale = 1.0
	defaultSize = Size(500, 500)

	def __init__(self, palette: Palette, config: SignalChartConfig):
		super().__init__()
		self.setWindowTitle("Signal Graph")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette
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
		self.show()

	def resizeEvent(self, event: QResizeEvent):
		newWidth = event.size().width()
		newHeight = event.size().height()
		self.updateGraph()
		self.svg.setGeometry(0, 0, newWidth, newHeight)

	def keyPressEvent(self, event: QKeyEvent):
		if event.key() == Qt.Key.Key_F:
			self.setWindowState(self.windowState() ^ Qt.WindowState.WindowFullScreen)
		if event.key() == Qt.Key.Key_S:
			self.sortMethodIndex = (self.sortMethodIndex + 1) % len(self.sortMethods)
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
