import os
import urllib.request


def fetchFontRomsIfNeeded():
	"""Download the HP1345A font files if they don't exist"""

	baseUrl = "https://phk.freebsd.dk/_downloads"
	roms = {
		"01347-80012.bin": f"{baseUrl}/a89c073235ca9c2b13d657173d32bf78/01347-80012.bin",
		"1816-1500.bin": f"{baseUrl}/2355976608a6359335e30a88e181f1fc/1816-1500.bin",
		"01347-80010.bin": f"{baseUrl}/13f169d8d8dff52497dca435d649f3d0/01347-80010.bin",
	}

	for rom, url in roms.items():
		if not os.path.isfile(f"./font/{rom}"):
			print(f"ROM file missing, downloading {rom}...")
			urllib.request.urlretrieve(url, f"./font/{rom}")
