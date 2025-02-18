from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QByteArray, pyqtSignal
from PyQt6.QtGui import QResizeEvent

from font.hp1345Font import Font
from font.mksvgs import makeSvgString, makeTextGroup
from misc.size import Size
from misc.config import RawMessageConfig
from palettes.palette import Palette


class RawMessageWindow(QMainWindow):
	"""Window for displaying raw messages"""

	textScale = 1.0
	satelliteReceivedEvent = pyqtSignal()
	defaultSize = Size(700, 500)

	def __init__(self, palette: Palette, config: RawMessageConfig):
		super().__init__()
		self.setWindowTitle("Raw Messages")
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette
		self.config = config

		self.satelliteReceivedEvent.connect(self.updateMessageLog)
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

		self.svg = QSvgWidget(parent=self)
		self.svg.load(QByteArray(svgStr.encode()))
		self.svg.setGeometry(0, 0, width, height)

		self.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))
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
		(newGroup, _, _) = makeTextGroup(
			self.svgFont,
			message,
			scale=self.textScale,
			fontThickness=self.config.fontThickness,
			fontColour=self.customPalette.foreground,
		)
		self.messageSvgGroups.insert(0, newGroup)
		self.messageSvgGroups.pop()

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
		self.svg.load(QByteArray(svgToDisplay.encode()))
		self.svg.setGeometry(0, 0, newWidth, int(newHeight))
