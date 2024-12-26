from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QResizeEvent, QKeyEvent
from mapdata.maps import readBaseSvg, addSatellites, prepareInitialSvg, focusOnPoint, saveToTempFile, MapConfig
from gnss.satellite import SatelliteInView
from palettes.palette import Palette

class MapWindow(QMainWindow):
	"""Configurable map window"""
	satelliteReceivedEvent = pyqtSignal()
	defaultWidth = 700
	defaultHeight = 500

	def __init__(self, palette: Palette, windowConfig: MapConfig, multiScreen: bool, windowIndex: int):
		super().__init__()

		self.windowConfig = windowConfig
		self.customPalette = palette
		self.latestSatellites = []

		self.latitude = 0
		self.longitude = 0

		self.baseSvg = readBaseSvg()
		self.initialSvg = self.generateNewMap()
		self.svgFile = saveToTempFile(self.initialSvg)
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, self.defaultWidth, self.defaultHeight)

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)
		self.handleMultiScreen(multiScreen)

		self.setWindowTitle("GNSS War Room")
		self.setGeometry(self.defaultWidth * windowIndex, 100, self.defaultWidth, self.defaultHeight)
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

	def generateNewMap(self):
		mapSvg = prepareInitialSvg(self.baseSvg, self.customPalette, self.windowConfig)
		mapSvg = focusOnPoint(mapSvg, self.windowConfig, self.defaultWidth, self.defaultHeight)
		return mapSvg

	def updateMap(self):
		"""Update the map with newest data"""
		mapSvg = addSatellites(
			self.initialSvg,
			self.latestSatellites,
			self.windowConfig,
			self.customPalette,
			self.latitude,
			self.longitude
		)
		mapSvg = focusOnPoint(mapSvg, self.windowConfig, self.map.width(), self.map.height())
		return saveToTempFile(mapSvg)

	def handleMultiScreen(self, multiScreen: bool):
		if multiScreen:
			self.showFullScreen()
		else:
			self.show()

	def resizeEvent(self, event: QResizeEvent):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()

		with open(self.svgFile, "r", encoding="utf8") as f:
			mapSvg = f.read()

		mapSvg = focusOnPoint(mapSvg, self.windowConfig, newX, newY)
		self.svgFile = saveToTempFile(mapSvg)

		self.map.load(self.svgFile)
		self.map.setGeometry(0, 0, newX, newY)

	def moveMapBy(self, lat: float, long: float):
		"""Move the map by a given amount"""
		self.windowConfig.focusLat += lat
		self.windowConfig.focusLong += long

		with open(self.svgFile, "r", encoding="utf8") as f:
			mapSvg = f.read()

		mapSvg = focusOnPoint(mapSvg, self.windowConfig, self.map.width(), self.map.height())
		self.svgFile = saveToTempFile(mapSvg)

		self.map.load(self.svgFile)
		self.map.setGeometry(0, 0, self.map.width(), self.map.height())

	# key bindings
	def keyPressEvent(self, event: QKeyEvent):
		"""Handle keybinds"""
		toMove = 2 / self.windowConfig.scaleFactor
		if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
			toMove *= 5

		if event.key() == Qt.Key.Key_W:
			self.moveMapBy(toMove, 0)
		if event.key() == Qt.Key.Key_S:
			self.moveMapBy(-toMove, 0)
		if event.key() == Qt.Key.Key_A:
			self.moveMapBy(0, -toMove)
		if event.key() == Qt.Key.Key_D:
			self.moveMapBy(0, toMove)

	def onNewData(self, satellites: list[SatelliteInView], latitude: float, longitude: float):
		"""Handle new satellite data"""
		self.latestSatellites = satellites.copy()
		self.latitude = latitude
		self.longitude = longitude
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		self.svgFile = self.updateMap()
		self.map.load(self.svgFile)
