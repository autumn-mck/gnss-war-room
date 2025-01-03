import os
import tempfile
import urllib.request

def saveToTempFile(string: str) -> str:
	"""Save a string to a temporary file and return its file path."""
	with tempfile.NamedTemporaryFile(delete=False) as temp:
		with open(temp.name, "w", encoding="utf8") as f:
			f.write(string)
	return temp.name

def fetchHp1345FilesIfNeeded():
	"""Download the HP1345A font files if they don't exist"""
	if os.path.isfile("./font/01347-80012.bin"):
		return

	print("Downloading HP1345 font files...")
	charRomUrl = "https://phk.freebsd.dk/_downloads/a89c073235ca9c2b13d657173d32bf78/01347-80012.bin"
	charIndexRomUrl = "https://phk.freebsd.dk/_downloads/2355976608a6359335e30a88e181f1fc/1816-1500.bin"
	firmwareRomUrl = "https://phk.freebsd.dk/_downloads/13f169d8d8dff52497dca435d649f3d0/01347-80010.bin"

	urllib.request.urlretrieve(charRomUrl, "./font/01347-80012.bin")
	urllib.request.urlretrieve(charIndexRomUrl, "./font/1816-1500.bin")
	urllib.request.urlretrieve(firmwareRomUrl, "./font/01347-80010.bin")
	print("Done downloading HP1345 font files")

class Size:
	"""A class for storing a size"""
	def __init__(self, width: float, height: float):
		self.width = width
		self.height = height
