import threading
import time

from PyQt6.QtCore import QByteArray, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QApplication, QMainWindow

from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from palettes.palette import Palette


class StartupWindow(QMainWindow):
	"""Window for displaying the startup sequence"""

	refreshSignal = pyqtSignal()

	def __init__(self, palette: Palette, app: QApplication):
		super().__init__()
		self.setWindowTitle("...")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")

		self.app = app
		self.customPalette = palette

		self.svgFont = Font()
		self.svg = QSvgWidget(parent=self)

		self.refreshSignal.connect(self.refresh)
		self.counter = 0
		self.stage = 0
		self.currentText = self.stageToText(self.stage)

		self.refreshThread = threading.Thread(target=self.backgroundThread)
		self.refreshThread.start()

	def stageToText(self, stage: int):
		match stage:
			case 0:
				return """LAUNCH ORDER CONFIRMED

TARGET SELECTION:         COMPLETE
TIME ON TARGET SEQUENCE:  COMPLETE
YIELD SELECTION:          COMPLETE

E_N_A_B_L_E_ _M_I_S_S_I_L_E_S_

LAUNCH TIME: BEGIN COUNTDOWN          """.replace("\n", "\n\r")
			case 1:
				return """WOPR EXECUTION ORDER
K.36.948.3

PART ONE: R O N C T T L
PART TWO: 07:20:35

LAUNCH CODE: D L G 2 2 0 9 T X

LAUNCH ORDER CONFIRMED
>_>_ _L_A_U_N_C_H_ _<_<_               """.replace("\n", "\n\r")
			case _:
				self.stage = -1
				return ""

	def backgroundThread(self):
		while self.stage >= 0:
			self.refreshSignal.emit()
			time.sleep(0.03)

	def refresh(self):
		"""Update the text on the window to the next character/stage"""
		self.counter += 1
		self.currentText = self.stageToText(self.stage)

		if self.stage == -1:
			time.sleep(0.1)
			windows = self.app.topLevelWidgets()
			for window in windows:
				window.close()

			self.close()
			return

		textSoFar = self.currentText[: self.counter]
		(svgStr, width, height) = makeSvgString(
			self.svgFont,
			textSoFar.encode("utf-8"),
			fontColour=self.customPalette.continentsBorder,
			fontThickness=2,
		)

		self.svg.load(QByteArray(svgStr.encode()))
		self.svg.setGeometry(0, 0, width, height)

		if self.counter == len(self.currentText):
			self.counter = 0
			self.stage += 1
