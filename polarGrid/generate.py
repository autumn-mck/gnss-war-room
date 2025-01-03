from palettes.palette import Palette


def readBasePolarGrid() -> str:
	with open("polarGrid/polar.svg", "r", encoding="utf8") as f:
		return f.read()


def prepareIntialPolarGrid(svgData: str, palette: Palette) -> str:
	"""Apply color palette to the SVG and add satellite positions"""
	svgData = svgData.replace('viewBox="0 0 94 94"', 'viewBox="-2 -2 98 98"')
	svgData = svgData.replace('fill="#fff"', f'fill="{palette.background}"')
	svgData = svgData.replace('stroke="#aaa"', f'stroke="{palette.polarGrid}"')
	svgData = svgData.replace('stroke="#000"', f'stroke="{palette.polarGrid}" style="display:none"')

	return svgData
