from collections import defaultdict

from font.hp1345Font import Font
from font.mksvgs import makeTextGroup
from gnss.satellite import SatelliteInView, colourForNetwork
from misc.config import SignalChartConfig
from palettes.palette import Palette


def generateYTick(
	settings: SignalChartConfig,
	palette: Palette,
	chartHeight: float,
	markerCount: int,
	currentMarker: int,
) -> str:
	"""That short horizontal line off the left axis"""
	return f"""<line
		x1='{settings.marginLeft - settings.markerWidth - settings.markerStrokeWidth / 2}'
		y1='{settings.marginTop + currentMarker * chartHeight / markerCount}'
		x2='{settings.marginLeft - settings.markerStrokeWidth / 2}'
		y2='{settings.marginTop + currentMarker * chartHeight / markerCount}'
		stroke='{palette.foreground}' stroke-width='{settings.markerStrokeWidth}' />\n"""


def generateYLabel(
	settings: SignalChartConfig,
	palette: Palette,
	font: Font,
	chartHeight: float,
	markerCount: int,
	currentMarker: int,
) -> str:
	"""Generate text indicating the given y tick"""
	textToDisplay = f"{int(settings.maxValue - (settings.markerStep * currentMarker))}"
	textSvg, textWidth, textHeight = makeTextGroup(
		font, textToDisplay.encode("ascii"), fontThickness=2, fontColour=palette.foreground
	)
	scaleTextBy = 0.4

	textWidth *= scaleTextBy
	textHeight *= scaleTextBy

	translateX = settings.marginLeft - textWidth
	translateY = settings.marginTop + currentMarker * chartHeight / markerCount - textHeight / 2

	return f"""<g transform='translate({translateX}, {translateY}) scale({scaleTextBy})'>
		{textSvg}
	</g>\n"""


def generateAxisLines(
	settings: SignalChartConfig, palette: Palette, chartWidth: float, chartHeight: float
) -> str:
	"""Generate the axis lines at the left and bottom of the graph"""
	leftX = settings.marginLeft - settings.markerStrokeWidth / 2
	rightX = settings.marginLeft + chartWidth - settings.markerStrokeWidth / 2

	topY = settings.marginTop - settings.markerStrokeWidth / 2
	bottomY = chartHeight + settings.marginTop + settings.markerStrokeWidth / 2

	return f"""<line
			x1='{leftX}'
			y1='{topY}'
			x2='{leftX}'
			y2='{bottomY}'
			stroke='{palette.foreground}'
			stroke-width='{settings.markerStrokeWidth}' />
		<line
			x1='{leftX}'
			y1='{bottomY}'
			x2='{rightX}'
			y2='{bottomY}'
			stroke='{palette.foreground}'
			stroke-width='{settings.markerStrokeWidth}' />
		"""


def generateScale(
	settings: SignalChartConfig,
	palette: Palette,
	font: Font,
	chartHeight: float,
	chartWidth: float,
	satellites: list[SatelliteInView],
) -> str:
	"""Generate the axis and scale with the given options"""
	scale = generateAxisLines(settings, palette, chartWidth, chartHeight)

	markerCount = int((settings.maxValue - settings.minValue) / settings.markerStep)

	_, _, charHeight = makeTextGroup(font, "0".encode("ascii"), fontThickness=2, border=0)
	step = 1
	charsCanFit = chartHeight / (charHeight)
	if charsCanFit < markerCount:
		step = 2

	for markerIndex in range(0, markerCount + 1, step):
		scale += generateYTick(settings, palette, chartHeight, markerCount, markerIndex)
		scale += generateYLabel(settings, palette, font, chartHeight, markerCount, markerIndex)

	if shouldLabelXAxis(satellites, font, chartWidth):
		scale += generateXLabels(settings, palette, font, chartWidth, chartHeight, satellites)
	return scale


def shouldLabelXAxis(satellites: list[SatelliteInView], font: Font, availableWidth: float) -> bool:
	"""Check if the x-axis should be labelled"""
	_, charWidth, _ = makeTextGroup(font, "0".encode("ascii"), fontThickness=2)
	charsCanFit = availableWidth / (charWidth - 10)
	return len(satellites) < charsCanFit * 2


def generateXLabels(
	settings: SignalChartConfig,
	palette: Palette,
	font: Font,
	chartWidth: float,
	chartHeight: float,
	satellites: list[SatelliteInView],
) -> str:
	"""Generate the x-axis labels"""
	if len(satellites) == 0:
		return ""

	labels = ""
	for index, satellite in enumerate(satellites):
		labels += generateXLabel(
			settings, palette, font, chartWidth, chartHeight, index, len(satellites), satellite
		)
	return labels


def generateXLabel(
	settings: SignalChartConfig,
	palette: Palette,
	font: Font,
	chartWidth: float,
	chartHeight: float,
	index: int,
	numSatellites: int,
	satellite: SatelliteInView,
) -> str:
	"""Generate the x-axis label for the given satellite"""
	barGap = chartWidth / 100
	barWidth = chartWidth / numSatellites - barGap

	labelText = f"{satellite.prnNumber}"
	labelTextSvg, labelWidth, labelHeight = makeTextGroup(
		font, labelText.encode("ascii"), fontThickness=2, fontColour=palette.foreground
	)
	scaleTextBy = 0.4

	labelWidth *= scaleTextBy
	labelHeight *= scaleTextBy

	translateX = (
		settings.marginLeft + index * chartWidth / numSatellites - labelWidth / 2 + barWidth / 2
	)
	translateY = settings.marginTop + chartHeight

	return f"""<g transform='translate({translateX}, {translateY}) scale({scaleTextBy})'>
		{labelTextSvg}
	</g>\n"""


def generateBar(
	settings: SignalChartConfig,
	palette: Palette,
	satellite: SatelliteInView,
	chartHeight: float,
	barIndex: int,
	barWidth: float,
	barGap: float,
) -> str:
	"""Generate the bar for the given satellite's SNR"""

	height = (
		chartHeight * (satellite.snr - settings.minValue) / (settings.maxValue - settings.minValue)
	)

	return f"""<rect
	x='{barIndex * barWidth + barGap * barIndex + settings.marginLeft}'
	y='{chartHeight - height + settings.marginTop}'
	width='{barWidth}'
	height='{height}'
	fill='{colourForNetwork(satellite.network, palette)}' />"""


def generateBars(
	settings: SignalChartConfig,
	palette: Palette,
	satellites: list[SatelliteInView],
	chartHeight: float,
	chartWidth: float,
) -> str:
	"""Generate the bars for the given satellite's SNRs"""
	barGap = chartWidth / 100
	barWidth = chartWidth / len(satellites) - barGap
	return "\n".join(
		generateBar(settings, palette, satellite, chartHeight, barsDrawn, barWidth, barGap)
		for barsDrawn, satellite in enumerate(satellites)
	)


def sortSatellitesByNetworkThenPrn(satellites: list[SatelliteInView]):
	"""Order the given satellites, first by which network they belong to, then their PRN"""
	satellitesByNetwork: dict[str, list[SatelliteInView]] = defaultdict(list)
	for satellite in satellites:
		satellitesByNetwork[satellite.network].append(satellite)

	satellites = []
	for satellitesInNetwork in satellitesByNetwork.values():
		satellites.extend(sortSatellitesByPrn(satellitesInNetwork))

	return satellites


def sortSatellitesByPrn(satellites: list[SatelliteInView]) -> list[SatelliteInView]:
	return sorted(satellites, key=lambda satellite: int(satellite.prnNumber))


def generateBarChart(
	settings: SignalChartConfig,
	palette: Palette,
	font: Font,
	satellites: list[SatelliteInView],
	availableWidth: float,
	availableHeight: float,
) -> str:
	"""Generate a full SVG SNR bar chart of the given satellites"""
	if not settings.countUntrackedSatellites:
		satellites = [satellite for satellite in satellites if satellite.snr != 0]

	if len(satellites) == 0:
		return f"<svg version='1.1' viewBox='0 0 {availableWidth} {availableHeight}'></svg>"

	satellites = sortSatellitesByNetworkThenPrn(satellites)

	chartWidth = availableWidth - settings.marginLeft - settings.marginRight
	chartHeight = availableHeight - settings.marginTop - settings.marginBottom

	chartContents = generateScale(settings, palette, font, chartHeight, chartWidth, satellites)
	chartContents += generateBars(settings, palette, satellites, chartHeight, chartWidth)

	return f"""<svg version='1.1' viewBox='0 0 {availableWidth} {availableHeight}'>
		{chartContents}
	</svg>"""
