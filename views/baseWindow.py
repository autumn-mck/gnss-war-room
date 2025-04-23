from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QMainWindow

from misc.size import Size
from palettes.palette import Palette


class BaseWindow(QMainWindow):
	"""Window for displaying the positions of satellites"""

	satelliteReceivedEvent = pyqtSignal()
	defaultSize = Size(500, 500)

	def __init__(self, palette: Palette):
		super().__init__()

		self.customPalette = palette

		self.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

	def keyPressEvent(self, event: QKeyEvent | None):
		"""Handle keybinds"""
		super().keyPressEvent(event)
		if event is None:
			return
		if event.key() == Qt.Key.Key_F:
			self.setWindowState(self.windowState() ^ Qt.WindowState.WindowFullScreen)
