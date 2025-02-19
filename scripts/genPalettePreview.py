from typing import Any

from palettes.palette import loadPalette


def main():
	"""Generate a preview of the palettes"""
	palette = loadPalette("warGames")

	squareSize = 100
	gapSize = 5

	svg = ""

	coloursToIgnore = ["#ff0000", "#FF0000"]
	attributesToIgnore = ["water"]

	count = 0
	coloursAlreadyUsed = []
	(svg, count) = paletteForColoursInDict(
		palette.__dict__,
		coloursToIgnore,
		attributesToIgnore,
		count,
		gapSize,
		squareSize,
		coloursAlreadyUsed,
	)

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


def paletteForColoursInDict(
	colours: dict[str, Any],
	coloursToIgnore: list[str],
	attributesToIgnore: list[str],
	count: int,
	gapSize: int,
	squareSize: int,
	coloursAlreadyUsed: list[str],
) -> tuple[str, int]:
	"""Generate rectangles for each colour in the given dict"""
	svg = ""
	for key, value in colours.items():
		if key in attributesToIgnore:
			continue
		if value in coloursAlreadyUsed:
			continue
		if value in coloursToIgnore:
			continue
		if isinstance(value, str):
			# value = value.lower()
			coloursAlreadyUsed.append(value)
			svg += f"""<rect
			x="{(squareSize + gapSize) * count + gapSize}" y="{gapSize}"
			width="{squareSize}" height="{squareSize}"
			fill="{value}" />\n"""
			count += 1
		elif isinstance(value, dict):
			(svgExtra, count) = paletteForColoursInDict(
				value,
				coloursToIgnore,
				attributesToIgnore,
				count,
				gapSize,
				squareSize,
				coloursAlreadyUsed,
			)
			svg += svgExtra

	return (svg, count)


if __name__ == "__main__":
	main()
