from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMainWindow

from misc.config import GlobeConfig
from misc.size import Size
from palettes.palette import Palette


class GlobeWindow(QMainWindow):
	"""Globe window using a webview"""

	defaultSize = Size(500, 500)

	def __init__(self, palette: Palette, config: GlobeConfig):
		super().__init__()
		self.setWindowTitle("Globe")
		self.setGeometry(0, 0, int(self.defaultSize.width), int(self.defaultSize.height))
		self.setStyleSheet(f"background-color: {palette.background}; color: {palette.foreground};")
		self.customPalette = palette
		self.config = config

		webView = QWebEngineView()
		# gives a type error but it works
		webView.page().profile().setHttpUserAgent("WOPR")  # type: ignore

		webView.load(QUrl(config.url))

		self.setCentralWidget(webView)

	def keyPressEvent(self, event: QKeyEvent):
		if event.key() == Qt.Key.Key_F:
			self.setWindowState(self.windowState() ^ Qt.WindowState.WindowFullScreen)
