from config import MiscStatsConfig
from font.hp1345Font import Font
from font.mksvgs import makeSvgString
from map.cities import findNearestCity
from gnss.nmea import GnssData
from palettes.palette import Palette


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
	nearestCity = findNearestCity(data.latitude, data.longitude)

	strToDisplay = f"Lat: {data.latitude:.6f}\n\rLong: {data.longitude:.6f}\n\r"
	strToDisplay += f"Date: {data.date.strftime('%Y-%m-%d')}\n\r"
	strToDisplay += f"Time: {data.date.strftime('%H:%M:%S')}\n\r"
	strToDisplay += f"City: {nearestCity}\n\r"
	strToDisplay += f"Altitude: {data.altitude:.1f}\n\r"
	strToDisplay += f"Geoid Separation: {data.geoidSeparation:.1f}\n\r"
	strToDisplay += f"PDOP: {data.pdop:.2f} ({classifyDOP(data.pdop)})\n\r"
	strToDisplay += f"HDOP: {data.hdop:.2f} ({classifyDOP(data.hdop)})\n\r"
	strToDisplay += f"VDOP: {data.vdop:.2f} ({classifyDOP(data.vdop)})\n\r"
	strToDisplay += f"Fix Quality: {data.fixQuality} ({classifyFixQuality(data.fixQuality)})"

	(svgStr, width, height) = makeSvgString(
		font,
		strToDisplay.encode("ascii"),
		fontThickness=config.fontThickness,
		fontColour=palette.foreground,
	)
	return (svgStr, width, height)
