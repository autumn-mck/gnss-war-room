from font.hp1345Font import Font
from font.mksvgs import makeTextGroup
from gnss.satellite import nameToNetworkCode
from misc.config import MapConfig
from misc.size import Size
from palettes.palette import Palette
from views.map.cities import getCities
from views.map.gallStereographic import latLongToGallStereographic


def readBaseMap() -> str:
	"""Read the base SVG map file."""
	with open("views/map/1981.svg", "r", encoding="utf8") as f:
		return f.read()


def getMapSize() -> Size:
	return Size(3213.05005, 2468.23999)


def prepareInitialMap(mapSvg: str, palette: Palette, options: MapConfig) -> tuple[str, Size]:
	"""Apply color palette and other options to the SVG map."""
	mapSize = getMapSize()

	# cities
	if not options.hideCities:
		mapSvg = mapSvg.replace("</svg>", genCitiesGroup(mapSize, options, palette) + "\n</svg>")

	# add comment for where satellites will go
	mapSvg = mapSvg.replace("</svg>", "\n<!-- satellites go here -->\n</svg>")

	# key (will be hidden later if needed)
	(keyStr, keySize) = genKey(palette)
	mapSvg = mapSvg.replace("</svg>", keyStr + "\n</svg>")

	# continent border width
	continentBorderWidth = 6 / options.scaleFactor
	admin0BorderWidth = 2 / options.scaleFactor

	# admin0 borders
	mapSvg = mapSvg.replace(
		".st2{fill:none;stroke:#000000;", f".st2{{fill:none;stroke:{palette.admin0Border};"
	)
	mapSvg = mapSvg.replace(".st2{", f".st2{{stroke-width:{admin0BorderWidth};")

	# continent borders
	mapSvg = mapSvg.replace("stroke-width:2;", f"stroke-width:{continentBorderWidth};")
	mapSvg = mapSvg.replace(
		".st4{fill:none;stroke:#000000;", f".st4{{fill:none;stroke:{palette.continentsBorder};"
	)

	if options.hideAdmin0Borders:
		mapSvg = mapSvg.replace(
			'g id="Admin_0_Polygon"', 'g id="Admin_0_Polygon" style="display:none"'
		)
		mapSvg = mapSvg.replace(
			'g id="Admin_x5F_0_x5F_lines"', 'g id="Admin_x5F_0_x5F_lines" style="display:none"'
		)

	# hide admin1 borders
	mapSvg = mapSvg.replace('g id="Admin_1_Polygon"', 'g id="Admin_1_Polygon" style="display:none"')
	mapSvg = mapSvg.replace(
		'g id="Admin_x5F_1_x5F_lines"', 'g id="Admin_x5F_1_x5F_lines" style="display:none"'
	)

	# hide rivers and lakes
	mapSvg = mapSvg.replace('g id="Rivers"', 'g id="Rivers" style="display:none"')
	mapSvg = mapSvg.replace('g id="Waterbodies"', 'g id="Waterbodies" style="display:none"')

	# hide metadata
	mapSvg = mapSvg.replace('g id="MetaData"', 'g id="MetaData" style="display:none"')
	return (mapSvg, keySize)


def genCitiesGroup(mapSize: Size, options: MapConfig, palette: Palette) -> str:
	"""Insert cities into the SVG"""
	cities = getCities()
	cityDataStr = f'\t<g id="Cities" fill="{palette.cities}">\n'
	for city in cities:
		cityLat = float(city[4])
		cityLong = float(city[5])
		[cityX, cityY] = latLongToGallStereographic(cityLat, cityLong, mapSize.width)
		cityX += mapSize.width / 2
		cityY += mapSize.height / 2

		radius = 5 / options.scaleFactor
		cityDataStr += f'\t\t<circle cx="{int(cityX)}" cy="{int(cityY)}" r="{radius}" />\n'

	cityDataStr += "\t</g>\n"

	return cityDataStr


def genKey(palette: Palette) -> tuple[str, Size]:
	"""Generate the key for the map"""
	svgFont = Font()

	group = ""

	maxWidth = 0
	heightSoFar = 0

	satelliteNetworks = list(palette.satelliteNetworks.items())
	satelliteNetworks.sort(key=lambda network: nameToNetworkCode(network[0]))

	for networkName, colour in satelliteNetworks:
		networkScale = 3.5

		(network, width, height) = makeTextGroup(
			svgFont,
			networkName.encode("ascii"),
			fontThickness=2,
			scale=networkScale,
			yOffset=int(heightSoFar / networkScale),
			fontColour=colour,
		)
		heightSoFar = height - 20
		maxWidth = max(maxWidth, width)
		group += "\n" + network

	heightSoFar += 20

	background = f"""<rect x="0" y="0"
	width="{maxWidth}" height="{heightSoFar}"
	fill="{palette.background}"
	stroke="{palette.foreground}" stroke-width="3" />"""
	group = background + "\n" + group

	group = '  <g id="Key">\n' + group + "  </g>\n"

	return (group, Size(maxWidth, heightSoFar))
