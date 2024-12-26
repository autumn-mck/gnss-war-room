from PyQt6.QtWidgets import QMainWindow

class MiscStatsWindow(QMainWindow):
	"""Window for displaying miscellaneous statistics"""
	def __init__(self, palette):
		super().__init__()
		self.setWindowTitle("Misc Stats")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette

		self.setGeometry(0, 0, 500, 500)
		self.show()
