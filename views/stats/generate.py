from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from gnss.nmea import GnssData
from misc.config import MiscStatsConfig
from palettes.palette import Palette
from views.map.cities import findNearestCityWithCache


def classifyDOP(dop: float) -> str:
	"""Classify the dilution of precision"""
	if dop < 1:
		return "Ideal"
	if dop < 2:
		return "Excellent"
	if dop < 5:
		return "Good"
	if dop < 10:
		return "Moderate"
	if dop < 20:
		return "Fair"
	return "Poor"


def classifyFixQuality(fixQuality: int) -> str:
	"""Classify the GGA fix quality"""
	if fixQuality == 0:
		return "Invalid"
	if fixQuality == 1:
		return "GPS"
	if fixQuality == 2:
		return "DGPS"
	print(f"Unknown fix quality: {fixQuality}")
	return "Unknown"


def generateStats(
	data: GnssData, palette: Palette, font: Font, config: MiscStatsConfig
) -> tuple[str, int, int]:
	"""Generate an SVG of stats for the given data"""
	nearestCity = findNearestCityWithCache(data.latitude, data.longitude)

	strToDisplay = f"""{chr(0x7f)} Location             {chr(0x7f)} DOP
Lat: {data.latitude:.8f}{chr(0x1a)}      PDOP: {data.pdop:.2f} ({classifyDOP(data.pdop)})
Long: {data.longitude:.8f}{chr(0x1a)}     HDOP: {data.hdop:.2f} ({classifyDOP(data.hdop)})
City: {nearestCity}          VDOP: {data.vdop:.2f} ({classifyDOP(data.vdop)})

{chr(0x7f)} Time                 {chr(0x7f)} Altitude
Time: {data.date.strftime("%H:%M:%S")}         Altitude: {data.altitude:.1f}{data.altitudeUnit.lower()}
Date: {data.date.strftime("%Y-%m-%d")}       Geoid: {data.geoidSeparation:.1f}{data.geoidSeparationUnit.lower()}

{chr(0x7f)} Stability
Interference: {data.interference:.2f}%
Fix Quality: {data.fixQuality} ({classifyFixQuality(data.fixQuality)})"""
	strToDisplay = "\n\r".join(strToDisplay.split("\n"))

	(svgStr, width, height) = makeSvgString(
		font,
		strToDisplay.encode("ascii"),
		fontThickness=config.fontThickness,
		fontColour=palette.foreground,
	)
	return (svgStr, width, height)
