from palettes.palette import loadPalette


def main():
	"""Generate a preview of the palettes"""
	palette = loadPalette("warGames")

	squareSize = 100
	gapSize = 5

	svg = ""

	coloursToIgnore = ["#ff0000"]
	attributesToIgnore = ["water"]

	count = 0
	coloursAlreadyUsed = []
	for attr, value in palette.__dict__.items():
		if attr in attributesToIgnore:
			continue

		if isinstance(value, str):
			value = value.lower()
			if value in coloursAlreadyUsed:
				continue
			if value in coloursToIgnore:
				continue
			coloursAlreadyUsed.append(value)
			svg += f"""<rect
			x="{(squareSize + gapSize) * count + gapSize}" y="{gapSize}"
			width="{squareSize}" height="{squareSize}"
			fill="{value}" />\n"""
			count += 1
		elif isinstance(value, dict):
			for key, value in value.items():
				if key in coloursToIgnore:
					continue
				if key in coloursAlreadyUsed:
					continue
				coloursAlreadyUsed.append(key)
				svg += f"""<rect
				x="{(squareSize + gapSize) * count + gapSize}" y="{gapSize}"
				width="{squareSize}" height="{squareSize}"
				fill="{value}" />\n"""
				count += 1

	width = gapSize + (squareSize + gapSize) * count
	height = gapSize * 2 + squareSize

	svg = f"""<?xml version="1.0" encoding="utf-8"?>
	<svg version="1.1"
	xmlns="http://www.w3.org/2000/svg"
	xmlns:xlink="http://www.w3.org/1999/xlink"
	width="{width}" height="{height}">
		<rect x="0" y="0" width="{width}" height="{height}" fill="#0" />
		{svg}
	</svg>"""

	with open("palettePreview.svg", "w", encoding="utf8") as f:
		f.write(svg)


if __name__ == "__main__":
	main()
