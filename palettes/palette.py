import json

def loadPalette(paletteName = "warGames") -> dict[str, str]:
	"""Load the palette with the given name."""
	with open(f"palettes/{paletteName}.json", "r") as f:
		palette = json.load(f)
	return palette