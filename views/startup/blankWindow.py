from PyQt6.QtWidgets import QMainWindow

from palettes.palette import Palette


class BlankWindow(QMainWindow):
	def __init__(self, palette: Palette):
		super().__init__()
		self.setWindowTitle("...")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
