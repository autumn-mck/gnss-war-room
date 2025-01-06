from config import SignalChartConfig
from font.hp1345Font import Font
from font.mksvgs import makeTextGroup
from gnss.satellite import SatelliteInView, colourForNetwork
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
		x1='{settings.marginLeft - settings.markerWidth  - settings.markerStrokeWidth / 2}'
		y1='{settings.marginTop + currentMarker * chartHeight / markerCount}'
		x2='{settings.marginLeft  - settings.markerStrokeWidth / 2}'
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
	settings: SignalChartConfig, palette: Palette, font: Font, chartHeight: float, chartWidth: float
) -> str:
	"""Generate the axis and scale with the given options"""
	scale = generateAxisLines(settings, palette, chartWidth, chartHeight)

	markerCount = int((settings.maxValue - settings.minValue) / settings.markerStep)
	for markerIndex in range(0, markerCount + 1):
		scale += generateYTick(settings, palette, chartHeight, markerCount, markerIndex)
		scale += generateYLabel(settings, palette, font, chartHeight, markerCount, markerIndex)
	return scale


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
	fill='{colourForNetwork(satellite.network, palette)}' />\n"""


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
	bars = ""
	barsDrawn = 0
	for satellite in satellites:
		bars += generateBar(settings, palette, satellite, chartHeight, barsDrawn, barWidth, barGap)
		barsDrawn += 1

	return bars


def sortSatellitesByNetworkThenPrn(satellites: list[SatelliteInView]):
	"""Order the given satellites, first by which network they belong to, then their PRN"""
	satellitesByNetwork: dict[str, list[SatelliteInView]] = {}
	for satellite in satellites:
		if satellite.network not in satellitesByNetwork:
			satellitesByNetwork[satellite.network] = []
		satellitesByNetwork[satellite.network].append(satellite)

	satellites = []
	for _, satellitesInNetwork in satellitesByNetwork.items():
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

	chartContents = generateScale(settings, palette, font, chartHeight, chartWidth)
	chartContents += generateBars(settings, palette, satellites, chartHeight, chartWidth)

	return f"""<svg version='1.1' viewBox='0 0 {availableWidth} {availableHeight}'>
		{chartContents}
	</svg>"""
