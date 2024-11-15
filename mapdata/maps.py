import math
import tempfile
from mapdata.cities import getCities

def readBaseSvg() -> str:
	with open("mapdata/1981.svg", "r") as f:
		return f.read()

def prepareSvg(svgData, palette, options = {
	"hideRivers": False,
	"hideAdmin0Borders": False,
	"hideAdmin1Borders": False,
	"hideLakes": False,
	"focusLat": 0.0,
	"focusLong": 0.0,
	"scaleFactor": 1
}) -> str:
	svgOrigWidth = 3213.05005
	svgOrigHeight = 2468.23999

	# cities
	if not options["hideCities"]:
		cities = getCities()
		cityDataStr = '<g id="Cities">'
		for city in cities:
			cityLat = float(city[4])
			cityLong = float(city[5])
			[cityX, cityY] = latLongToGallStereographic(cityLat, cityLong, svgOrigWidth)
			cityX += svgOrigWidth / 2
			cityY += svgOrigHeight / 2
			cityDataStr += f'<circle cx="{cityX}" cy="{cityY}" r="2" fill="{palette["cities"]}" />'

		cityDataStr += '</g></svg>'
		svgData = svgData.replace('</svg>', cityDataStr)

	# continent border width
	continentBorderWidth = 6 / options["scaleFactor"]
	admin0BorderWidth = 2 / options["scaleFactor"]

	# waterbodies
	svgData = svgData.replace('.st0{fill:#50C8F4;', f'.st0{{fill:{palette["water"]};')
	svgData = svgData.replace('.st3{fill:none;stroke:#50C8F4;', f'.st3{{fill:none;stroke:{palette["water"]};')

	# admin1 borders
	svgData = svgData.replace('.st1{fill:none;stroke:#808080;', f'.st1{{fill:none;stroke:{palette["admin1Border"]};')

	# admin0 borders
	svgData = svgData.replace('.st2{fill:none;stroke:#000000;', f'.st2{{fill:none;stroke:{palette["admin0Border"]};')
	svgData = svgData.replace('.st2{', f'.st2{{stroke-width:{admin0BorderWidth};')

	# continent borders
	svgData = svgData.replace('stroke-width:2;', f'stroke-width:{continentBorderWidth};');
	svgData = svgData.replace('.st4{fill:none;stroke:#000000;', f'.st4{{fill:none;stroke:{palette["continentsBorder"]};')

	# metadata
	svgData = svgData.replace('.st5{fill:#221F1F;', f'.st5{{fill:{palette["metadata"]};')
	svgData = svgData.replace('.st12{fill:none;stroke:#231F20;', f'.st12{{fill:none;stroke:{palette["metadata"]};')

	if options["hideAdmin0Borders"]:
		svgData = svgData.replace('g id="Admin_0_Polygon"', 'g id="Admin_0_Polygon" style="display:none"')
		svgData = svgData.replace('g id="Admin_x5F_0_x5F_lines"', 'g id="Admin_x5F_0_x5F_lines" style="display:none"')

	if options["hideAdmin1Borders"]:
		svgData = svgData.replace('g id="Admin_1_Polygon"', 'g id="Admin_1_Polygon" style="display:none"')
		svgData = svgData.replace('g id="Admin_x5F_1_x5F_lines"', 'g id="Admin_x5F_1_x5F_lines" style="display:none"')

	if options["hideRivers"]:
		svgData = svgData.replace('g id="Rivers"', 'g id="Rivers" style="display:none"')

	if options["hideLakes"]:
		svgData = svgData.replace('g id="Waterbodies"', 'g id="Waterbodies" style="display:none"')

	# hide metadata
	svgData = svgData.replace('g id="MetaData"', 'g id="MetaData" style="display:none"')
	return svgData

def saveTempSvg(svgData: str) -> str:
	temp = tempfile.NamedTemporaryFile(delete=False)
	with open(temp.name, "w") as f:
		f.write(svgData)
	return temp.name

def focusOnPoint(svgData, options, desiredWidth, desiredHeight) -> str:
	svgOrigWidth = 3213.05005
	svgOrigHeight = 2468.23999
	xOffset = -10

	match options["scaleMethod"]:
		case "constantScale":
			newWidth = desiredWidth / options["scaleFactor"] * 3
			newHeight = desiredHeight / options["scaleFactor"] * 3
		case "withWidth":
			newWidth = svgOrigWidth / options["scaleFactor"]
			newHeight = newWidth * desiredHeight / desiredWidth
		case "withHeight":
			newHeight = svgOrigHeight / options["scaleFactor"]
			newWidth = newHeight * desiredWidth / desiredHeight
		case "fit":
			if desiredWidth / svgOrigWidth < desiredHeight / svgOrigHeight:
				newWidth = svgOrigWidth / options["scaleFactor"]
				newHeight = newWidth * desiredHeight / desiredWidth
			else:
				newHeight = svgOrigHeight / options["scaleFactor"]
				newWidth = newHeight * desiredWidth / desiredHeight

	[projectedX, projectedY] = latLongToGallStereographic(options["focusLat"], options["focusLong"], svgOrigWidth)
	projectedX += svgOrigWidth / 2
	projectedY += svgOrigHeight / 2

	# inserting circle at focus point
	svgData = svgData.replace('</svg>', f'<circle cx="{projectedX}" cy="{projectedY}" r="2" fill="red" /></svg>')

	newX = projectedX - newWidth / 2
	newY = projectedY - newHeight / 2

	viewboxLen = len('viewBox="')
	newViewbox = f"{newX} {newY} {newWidth} {newHeight}"
	# find location of original viewbox
	viewBoxStart = svgData.find('viewBox="')
	viewBoxEnd = svgData.find('"', viewBoxStart + viewboxLen)

	return svgData[:viewBoxStart + viewboxLen] + newViewbox + svgData[viewBoxEnd:]


def latLongToGallStereographic(lat: float, long: float, mapWidth: float) -> tuple[float, float]:
	"""Convert latitude and longitude to Gall Stereographic coordinates."""
	longOffset = -10
	long += longOffset

	# wrap around the world as the map is not centered at 0
	if long < -180 - longOffset:
		long += 360
	elif long > 180 - longOffset:
		long -= 360

	R = mapWidth / (2 * math.pi)
	latRad = math.radians(lat)
	longRad = math.radians(long)

	x = R * longRad # the formula should divide by sqrt(2) here but for some reason that gives the wrong result
	y = -R * (math.sqrt(2) + 1) * math.tan(latRad / 2)

	return (x, y)