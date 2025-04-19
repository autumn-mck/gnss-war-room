from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

from misc.config import GlobeConfig
from misc.size import Size
from palettes.palette import Palette
from views.baseWindow import BaseWindow


class GlobeWindow(BaseWindow):
	"""Globe window using a webview"""

	def __init__(self, palette: Palette, config: GlobeConfig):
		super().__init__(palette)
		self.setWindowTitle("Globe")
		self.config = config

		webView = QWebEngineView()
		# gives a type error but it works
		webView.page().profile().setHttpUserAgent("WOPR")  # type: ignore

		webView.load(QUrl(config.url))

		self.setCentralWidget(webView)
