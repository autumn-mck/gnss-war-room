import random
import string
import threading
import time
from typing import ClassVar

from PyQt6.QtCore import QByteArray, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QApplication, QMainWindow

from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from palettes.palette import Palette


class StartupWindow(QMainWindow):
	"""Window for displaying the startup sequence"""

	refreshSignal = pyqtSignal()

	internalSignalChars: ClassVar[list] = [chr(0x08), chr(0x0C)]

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
		# char to be randomly replaced
		r = chr(0x09)

		match stage:
			case 0:
				return f"""
 WOPR BOOT SEQUENCE{chr(0x08)}

 checking system{chr(0x0C)}.{chr(0x0C)}.{chr(0x0C)}.{chr(0x0C)}
 minimum specs{chr(0x08)} OK{chr(0x0C)}{chr(0x0C)}
 inframaterialising (built 0.001%)
 enabling x-clacks-overhead
 accessing main security grid{chr(0x0C)}.{chr(0x0C)}.{chr(0x0C)}.{chr(0x0C)}
 enter logon: {chr(0x0C)}*{chr(0x0C)}*{chr(0x0C)}*{chr(0x0C)}*{chr(0x0C)}*{chr(0x0C)}*
{chr(0x08)}
 -- connection started --

 G_N_S_S_ _W_A_R_ _R_O_O_M_
 {chr(0x08)}{chr(0x08)}
""".replace("\n", "\n\r")
			case 1:
				return f"""
 WOPR EXECUTION ORDER
 K.36.948.3

 PART ONE: R O N C T T L
 PART TWO: 07:20:35

 LAUNCH CODE: {r} {r} {r} {r} {r} {r} {r} {r} {r}

 LAUNCH ORDER CONFIRMED
 >_>_ _L_A_U_N_C_H_ _<_<_{chr(0x08)}{chr(0x08)}{chr(0x08)}{chr(0x08)}
""".replace("\n", "\n\r")
			case 2:
				return f"""
 L_A_U_N_C_H_ _O_R_D_E_R_ _C_O_N_F_I_R_M_E_D_

 TARGET SELECTION:{chr(0x08)}           COMPLETE
 TIME ON TARGET SEQUENCE:{chr(0x08)}    COMPLETE
 SATELLITE TRACKING:{chr(0x08)}         COMPLETE

 E_N_A_B_L_E_ _M_I_S_S_I_L_E_S_{chr(0x08)}{chr(0x08)}

 STARTING:{chr(0x08)}   GLOBAL THERMONUCLEAR WAR
{chr(0x08)}{chr(0x08)}{chr(0x08)}
""".replace("\n", "\n\r")
			case _:
				self.stage = -1
				return ""

	def backgroundThread(self):
		while self.stage >= 0:
			self.tick()
			time.sleep(0.02)

	def tick(self):
		"""Update the text on the window to the next character/stage"""
		self.refreshSignal.emit()
		self.counter += 1
		if (
			self.counter < len(self.currentText) - 1
			and self.currentText[self.counter] in self.internalSignalChars
		):
			self.runCommand(self.currentText[self.counter])

	def runCommand(self, command: str):
		"""Attempt to interpret the given character as a command"""
		if command == chr(0x08):
			for _ in range(50):
				self.refreshSignal.emit()
				time.sleep(0.02)
		elif command == chr(0x0C):
			for _ in range(5):
				self.refreshSignal.emit()
				time.sleep(0.02)
		else:
			print(f"Unknown command: {command.encode()}")

	def refresh(self):
		"""Update the text on the window to the next character/stage"""
		self.currentText = self.stageToText(self.stage)

		if self.counter == len(self.currentText):
			self.counter = 0
			self.stage += 1

		if self.stage == -1:
			windows = self.app.topLevelWidgets()
			for window in windows:
				window.close()

			self.close()
			return

		currentChar = self.currentText[self.counter]
		while (currentChar in (" ", "_")) and self.counter < len(self.currentText):
			self.counter += 1
			currentChar = self.currentText[self.counter]

		if currentChar in string.ascii_letters + string.digits:
			textSoFar = self.currentText[: self.counter] + " _"
		else:
			textSoFar = self.currentText[: self.counter]

		textToDisplay = ""
		for char in textSoFar:
			if char == chr(0x09):
				textToDisplay += chr(0x41 + random.randint(0, 25))
			elif char in self.internalSignalChars:
				textToDisplay += ""
			else:
				textToDisplay += char

		(svgStr, width, height) = makeSvgString(
			self.svgFont,
			textToDisplay.encode("utf-8"),
			fontColour=self.customPalette.continentsBorder,
			fontThickness=2,
		)

		self.svg.load(QByteArray(svgStr.encode()))
		self.svg.setGeometry(0, 0, width, height)
