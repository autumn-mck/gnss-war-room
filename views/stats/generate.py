from itertools import zip_longest

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


def combineWithPadding(left: list[str], right: list[str], padToWidth: int) -> list[str]:
	output = []
	for leftLine, rightLine in zip_longest(left, right, fillvalue=""):
		paddedLeftLine = leftLine.ljust(padToWidth)
		output.append(f"{paddedLeftLine}{rightLine}")
	return output


def generateStats(
	data: GnssData, palette: Palette, font: Font, config: MiscStatsConfig
) -> tuple[str, int, int]:
	"""Generate an SVG of stats for the given data"""
	nearestCity = findNearestCityWithCache(data.latitude, data.longitude)

	location = [
		f"{chr(0x7f)} Location",
		f"Lat: {data.latitude:.8f}{chr(0x1a)}",
		f"Long: {data.longitude:.8f}{chr(0x1a)}",
		f"City: {nearestCity}",
	]

	time = [
		f"{chr(0x7f)} Time",
		f"Time: {data.date.strftime("%H:%M:%S")}",
		f"Date: {data.date.strftime("%Y-%m-%d")}",
	]

	snrSum = sum(sat.snr for sat in data.satellites)
	snrCount = len([sat for sat in data.satellites if sat.snr > 0]) or 1
	stability = [
		f"{chr(0x7f)} Stability",
		f"Interference: {data.interference:.2f}%",
		f"Fix Quality: {data.fixQuality} ({classifyFixQuality(data.fixQuality)})",
		f"Mean SNR: {snrSum / snrCount:.2f}",
	]

	dop = [
		f"{chr(0x7f)} DOP",
		f"PDOP: {data.pdop:.2f} ({classifyDOP(data.pdop)})",
		f"HDOP: {data.hdop:.2f} ({classifyDOP(data.hdop)})",
		f"VDOP: {data.vdop:.2f} ({classifyDOP(data.vdop)})",
	]

	altitude = [
		f"{chr(0x7f)} Altitude",
		f"Altitude: {data.altitude:.1f}{data.altitudeUnit.lower()}",
		f"Geoid: {data.geoidSeparation:.1f}{data.geoidSeparationUnit.lower()}",
	]

	padTo = 22
	locDop = combineWithPadding(location, dop, padTo)
	timeAlt = combineWithPadding(time, altitude, padTo)

	strToDisplay = f"""{"\n".join(locDop)}

{"\n".join(timeAlt)}

{"\n".join(stability)}"""
	strToDisplay = "\n\r".join(strToDisplay.split("\n"))

	(svgStr, width, height) = makeSvgString(
		font,
		strToDisplay.encode("ascii"),
		fontThickness=config.fontThickness,
		fontColour=palette.foreground,
	)
	return (svgStr, width, height)
