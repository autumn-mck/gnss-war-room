from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
from PyQt6.QtGui import QResizeEvent, QKeyEvent
from views.map.update import genSatelliteMapGroup, focusOnPoint
from views.map.generate import readBaseMap, prepareInitialMap
from misc.size import Size
from misc.config import MapConfig
from gnss.satellite import SatelliteInView
from palettes.palette import Palette


class MapWindow(QMainWindow):
	"""Configurable map window"""

	satelliteReceivedEvent = pyqtSignal()
	defaultSize = Size(700, 500)

	def __init__(self, palette: Palette, windowConfig: MapConfig):
		super().__init__()

		self.windowConfig = windowConfig
		self.customPalette = palette
		self.latestSatellites = []

		self.latitude = 0
		self.longitude = 0

		self.keyXMult = 0
		self.keyYMult = 1

		baseSvg = readBaseMap()

		(self.initialMap, self.keySize) = prepareInitialMap(baseSvg, palette, windowConfig)
		self.preFocusMap = self.initialMap
		self.map = QSvgWidget(parent=self)
		self.map.load(QByteArray(self.initialMap.encode()))
		self.map.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))

		self.satelliteReceivedEvent.connect(self.newSatelliteDataEvent)

		self.setWindowTitle("GNSS War Room")
		self.setGeometry(0, 100, int(self.defaultSize.width), int(self.defaultSize.height))
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.show()

	def updateMap(self):
		"""Update the map with newest data"""
		satelliteGroup = genSatelliteMapGroup(
			self.windowConfig,
			self.customPalette,
			self.latestSatellites,
			self.latitude,
			self.longitude,
		)
		mapSvg = self.initialMap.replace("<!-- satellites go here -->", satelliteGroup)
		self.preFocusMap = mapSvg
		mapSvg = focusOnPoint(
			mapSvg,
			self.windowConfig,
			Size(self.map.width(), self.map.height()),
			self.keySize,
			self.keyXMult,
			self.keyYMult,
		)
		return mapSvg

	def resizeEvent(self, event: QResizeEvent):
		"""Resize map when window is resized"""
		newX = event.size().width()
		newY = event.size().height()

		mapSvg = focusOnPoint(
			self.preFocusMap,
			self.windowConfig,
			Size(newX, newY),
			self.keySize,
			self.keyXMult,
			self.keyYMult,
		)

		self.map.load(QByteArray(mapSvg.encode()))
		self.map.setGeometry(0, 0, newX, newY)

	def moveMapBy(self, lat: float, long: float):
		"""Move the map by a given amount"""
		self.windowConfig.focusLat += lat
		self.windowConfig.focusLong += long

	# key bindings
	def keyPressEvent(self, event: QKeyEvent):
		"""Handle keybinds"""
		self.handleMoveMapKeys(event)
		self.handleMoveKeyKeys(event)
		self.handleScaleKeys(event)

		if event.key() == Qt.Key.Key_K:
			self.windowConfig.hideKey = not self.windowConfig.hideKey

		if event.key() == Qt.Key.Key_T:
			self.windowConfig.hideSatelliteTrails = not self.windowConfig.hideSatelliteTrails
			self.resetMapOnScale()

		if event.key() == Qt.Key.Key_X:
			self.windowConfig.hideAdmin0Borders = not self.windowConfig.hideAdmin0Borders
			self.resetMapOnScale()

		if event.key() == Qt.Key.Key_C:
			self.windowConfig.hideCities = not self.windowConfig.hideCities
			self.resetMapOnScale()

		mapSvg = focusOnPoint(
			self.preFocusMap,
			self.windowConfig,
			Size(self.map.width(), self.map.height()),
			self.keySize,
			self.keyXMult,
			self.keyYMult,
		)

		self.map.load(QByteArray(mapSvg.encode()))

	def handleMoveMapKeys(self, event: QKeyEvent):
		"""Handle keybinds for moving the map"""
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

	def handleMoveKeyKeys(self, event: QKeyEvent):
		"""Handle keybinds for moving the key"""
		keyMovement = 0.5
		if event.key() == Qt.Key.Key_Left:
			self.keyXMult -= keyMovement
		if event.key() == Qt.Key.Key_Right:
			self.keyXMult += keyMovement
		if event.key() == Qt.Key.Key_Up:
			self.keyYMult -= keyMovement
		if event.key() == Qt.Key.Key_Down:
			self.keyYMult += keyMovement

		self.keyXMult = max(0, min(1, self.keyXMult))
		self.keyYMult = max(0, min(1, self.keyYMult))

	def handleScaleKeys(self, event: QKeyEvent):
		"""Handle keybinds for scaling the map"""
		if event.key() == Qt.Key.Key_Q:
			self.windowConfig.scaleFactor *= 1.1
			self.resetMapOnScale()
		if event.key() == Qt.Key.Key_E:
			self.windowConfig.scaleFactor /= 1.1
			self.resetMapOnScale()

		scaleMethods = ["constantScale", "withWidth", "withHeight", "fit"]
		if event.key() == Qt.Key.Key_Z:
			currentScaleIndex = scaleMethods.index(self.windowConfig.scaleMethod)
			newScaleMethod = scaleMethods[(currentScaleIndex + 1) % len(scaleMethods)]
			self.windowConfig.scaleMethod = newScaleMethod

	def resetMapOnScale(self):
		"""Reset the map on scale to prevent any artifacts"""
		baseSvg = readBaseMap()
		(self.initialMap, self.keySize) = prepareInitialMap(
			baseSvg, self.customPalette, self.windowConfig
		)
		self.preFocusMap = self.initialMap
		self.newSatelliteDataEvent()

	def onNewData(self, satellites: list[SatelliteInView], latitude: float, longitude: float):
		"""Handle new satellite data"""
		self.latestSatellites = satellites
		self.latitude = latitude
		self.longitude = longitude
		self.satelliteReceivedEvent.emit()

	def newSatelliteDataEvent(self):
		newMap = self.updateMap()
		self.map.load(QByteArray(newMap.encode()))
