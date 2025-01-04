from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QResizeEvent
from config import RawMessageConfig

from font.hp1345Font import Font
from font.mksvgs import makeSvgString, makeTextGroup
from misc import Size, saveToTempFile
from palettes.palette import Palette


class RawMessageWindow(QMainWindow):
	"""Window for displaying raw messages"""

	satelliteReceivedEvent = pyqtSignal()
	textScale = 1.0

	def __init__(self, palette: Palette, config: RawMessageConfig):
		super().__init__()
		self.setWindowTitle("Raw Messages")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette
		self.config = config

		self.messages = [""] * config.numMessagesToKeep
		self.messageSvgGroups = [""] * config.numMessagesToKeep

		self.svgFont = Font()
		(_, charWidth, charHeight) = makeTextGroup(
			self.svgFont,
			"$".encode("ascii"),
			scale=self.textScale,
			fontThickness=self.config.fontThickness,
			border=0,
			fontColour=palette.foreground,
		)
		self.charSize = Size(charWidth, charHeight)

		(svgStr, width, height) = makeSvgString(
			self.svgFont,
			"Waiting for data...".encode("ascii"),
			fontColour=palette.foreground,
			fontThickness=2,
		)

		svgFile = saveToTempFile(svgStr)
		self.svg = QSvgWidget(svgFile, parent=self)
		self.svg.setGeometry(0, 0, width, height)

		self.satelliteReceivedEvent.connect(self.updateMessageLog)

		self.setGeometry(0, 0, 500, 500)
		self.show()

	def resizeEvent(self, event: QResizeEvent):
		"""Resize the window"""
		newWidth = event.size().width()
		oldWidth = self.svg.width()
		oldHeight = self.svg.height()
		newHeight = oldHeight * newWidth / oldWidth
		self.svg.setGeometry(0, 0, newWidth, int(newHeight))

	def onNewData(self, message: bytes):
		"""Update the raw message window with new data"""
		self.messages.insert(0, message.decode("utf-8"))
		self.messages.pop()

		(newGroup, _, _) = makeTextGroup(
			self.svgFont,
			message,
			scale=self.textScale,
			fontThickness=self.config.fontThickness,
			fontColour=self.customPalette.foreground,
		)
		self.messageSvgGroups.insert(0, newGroup)
		self.messageSvgGroups.pop()

		self.satelliteReceivedEvent.emit()

	def updateMessageLog(self):
		"""Update the displayed message log"""
		svgToDisplay = ""

		heightOfMessage = self.charSize.height + 15

		for i, messageSvgGroup in enumerate(self.messageSvgGroups):
			strToAdd = f"""<g transform="translate(0, {i * heightOfMessage})">
				{messageSvgGroup}
			</g>"""
			svgToDisplay += strToAdd

		charsWide = 75
		totalWidth = charsWide * self.charSize.width

		newWidth = self.svg.width()
		desiredHeight = int(heightOfMessage * len(self.messageSvgGroups))
		newHeight = desiredHeight * newWidth / totalWidth

		svgToDisplay = (
			f'<svg version="1.1" viewBox="0 0 {totalWidth} {desiredHeight}">{svgToDisplay}</svg>'
		)
		svgFile = saveToTempFile(svgToDisplay)
		self.svg.load(svgFile)
		self.svg.setGeometry(0, 0, newWidth, int(newHeight))
