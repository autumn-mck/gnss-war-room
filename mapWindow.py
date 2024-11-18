from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent, QKeyEvent
from mapdata.maps import readBaseSvg, prepareSvg, focusOnPoint, saveToTempFile, MapConfig
from palettes.palette import Palette

class MapWindow(QMainWindow):
	"""Configurable map window"""
	def __init__(self, palette: Palette, windowConfig: MapConfig, multiScreen: bool, windowIndex: int):
		super().__init__()

		defaultWidth = 700
		defaultHeight = 500

		self.windowConfig = windowConfig

		self.setWindowTitle("GNSS War Room")

		self.setGeometry(defaultWidth * windowIndex, 100, defaultWidth, defaultHeight)
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

		mapSvg = readBaseSvg()
		mapSvg = prepareSvg(mapSvg, palette, windowConfig)
		mapSvg = focusOnPoint(mapSvg, windowConfig, defaultWidth, defaultHeight)

		self.svgFile = saveToTempFile(mapSvg)
		self.map = QSvgWidget(self.svgFile, parent=self)
		self.map.setGeometry(0, 0, defaultWidth, defaultHeight)

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