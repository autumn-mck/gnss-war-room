from palettes.palette import Palette
from map.cities import getCities
from map.gallStereographic import latLongToGallStereographic
from config import MapConfig
from font.hp1345Font import Font
from font.mksvgs import makeTextGroup

def readBaseMap() -> str:
	"""Read the base SVG map file."""
	with open("map/1981.svg", "r", encoding="utf8") as f:
		return f.read()

def getMapSize() -> tuple[float, float]:
	return (3213.05005, 2468.23999)

def prepareInitialMap(mapSvg: str, palette: Palette, options: MapConfig) -> str:
	"""Apply color palette and other options to the SVG map."""
	mapWidth, mapHeight = getMapSize()

	# cities
	if not options.hideCities:
		mapSvg = mapSvg.replace('</svg>', genCitiesGroup(mapWidth, mapHeight, options, palette) + '\n</svg>')

	# add comment for where sattelites will go
	mapSvg = mapSvg.replace('</svg>', '\n<!-- satellites go here -->\n</svg>')

	# key
	if not options.hideKey:
		keyStr, _, _ = genKey(palette)
		mapSvg = mapSvg.replace('</svg>', keyStr + '\n</svg>')

	# continent border width
	continentBorderWidth = 6 / options.scaleFactor
	admin0BorderWidth = 2 / options.scaleFactor

	# waterbodies
	mapSvg = mapSvg.replace('.st0{fill:#50C8F4;', f'.st0{{fill:{palette.water};')
	mapSvg = mapSvg.replace('.st3{fill:none;stroke:#50C8F4;', f'.st3{{fill:none;stroke:{palette.water};')

	# admin1 borders
	mapSvg = mapSvg.replace('.st1{fill:none;stroke:#808080;', f'.st1{{fill:none;stroke:{palette.admin1Border};')

	# admin0 borders
	mapSvg = mapSvg.replace('.st2{fill:none;stroke:#000000;', f'.st2{{fill:none;stroke:{palette.admin0Border};')
	mapSvg = mapSvg.replace('.st2{', f'.st2{{stroke-width:{admin0BorderWidth};')

	# continent borders
	mapSvg = mapSvg.replace('stroke-width:2;', f'stroke-width:{continentBorderWidth};')
	mapSvg = mapSvg.replace('.st4{fill:none;stroke:#000000;', f'.st4{{fill:none;stroke:{palette.continentsBorder};')

	if options.hideAdmin0Borders:
		mapSvg = mapSvg.replace('g id="Admin_0_Polygon"', 'g id="Admin_0_Polygon" style="display:none"')
		mapSvg = mapSvg.replace('g id="Admin_x5F_0_x5F_lines"', 'g id="Admin_x5F_0_x5F_lines" style="display:none"')

	if options.hideAdmin1Borders:
		mapSvg = mapSvg.replace('g id="Admin_1_Polygon"', 'g id="Admin_1_Polygon" style="display:none"')
		mapSvg = mapSvg.replace('g id="Admin_x5F_1_x5F_lines"', 'g id="Admin_x5F_1_x5F_lines" style="display:none"')

	if options.hideRivers:
		mapSvg = mapSvg.replace('g id="Rivers"', 'g id="Rivers" style="display:none"')

	if options.hideLakes:
		mapSvg = mapSvg.replace('g id="Waterbodies"', 'g id="Waterbodies" style="display:none"')

	# hide metadata
	mapSvg = mapSvg.replace('g id="MetaData"', 'g id="MetaData" style="display:none"')
	return mapSvg

def genCitiesGroup(svgOrigWidth: float, svgOrigHeight: float, options: MapConfig, palette: Palette) -> str:
	"""Insert cities into the SVG"""
	cities = getCities()
	cityDataStr = f'\t<g id="Cities" fill="{palette.cities}">\n'
	for city in cities:
		cityLat = float(city[4])
		cityLong = float(city[5])
		[cityX, cityY] = latLongToGallStereographic(cityLat, cityLong, svgOrigWidth)
		cityX += svgOrigWidth / 2
		cityY += svgOrigHeight / 2

		radius = 5 / options.scaleFactor
		cityDataStr += f'\t\t<circle cx="{int(cityX)}" cy="{int(cityY)}" r="{radius}" />\n'

	cityDataStr += '\t</g>\n'

	return cityDataStr

def genKey(palette: Palette) -> tuple[str, int, int]:
	"""Generate the key for the map"""
	svgFont = Font()

	group = ''

	maxWidth = 0
	heightSoFar = 0

	for networkName, colour in palette.satelliteNetworks.items():
		networkScale = 3.5

		network, width, height = makeTextGroup(svgFont,
			networkName.encode('ascii'),
			fontThickness=2,
			scale=networkScale,
			yOffset=int(heightSoFar / networkScale),
			fontColour=colour)
		heightSoFar = height - 20
		maxWidth = max(maxWidth, width)
		group += "\n" + network

	heightSoFar += 20

	background = f"""<rect x="0" y="0"
	width="{maxWidth}" height="{heightSoFar}"
	fill="{palette.background}"
	stroke="{palette.foreground}" stroke-width="3" />"""
	group = background + "\n" + group

	group = '  <g id="Key">\n' + group + '  </g>\n'

	return group, int(maxWidth), int(heightSoFar)
