import os
import urllib.request
from dataclasses import dataclass
from PyQt6.QtCore import QByteArray


def svgToQByteArray(svg: str) -> QByteArray:
	return QByteArray(svg.encode("utf-8"))


def fetchHp1345FilesIfNeeded():
	"""Download the HP1345A font files if they don't exist"""
	if os.path.isfile("./font/01347-80012.bin"):
		return

	print("Downloading HP1345 font files...")
	charRomUrl = (
		"https://phk.freebsd.dk/_downloads/a89c073235ca9c2b13d657173d32bf78/01347-80012.bin"
	)
	charIndexRomUrl = (
		"https://phk.freebsd.dk/_downloads/2355976608a6359335e30a88e181f1fc/1816-1500.bin"
	)
	firmwareRomUrl = (
		"https://phk.freebsd.dk/_downloads/13f169d8d8dff52497dca435d649f3d0/01347-80010.bin"
	)

	urllib.request.urlretrieve(charRomUrl, "./font/01347-80012.bin")
	urllib.request.urlretrieve(charIndexRomUrl, "./font/1816-1500.bin")
	urllib.request.urlretrieve(firmwareRomUrl, "./font/01347-80010.bin")
	print("Done downloading HP1345 font files")


@dataclass
class Size:
	width: float
	height: float
