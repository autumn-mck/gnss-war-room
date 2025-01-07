from dataclasses import dataclass
import pyjson5
from dataclass_wizard import JSONWizard


@dataclass
class MapConfig(JSONWizard):
	"""Configuration for the map."""

	scaleFactor: float = 1
	scaleMethod: str = "fit"
	hideKey: bool = False

	focusLat: float = 0
	focusLong: float = 10

	hideCities: bool = True
	hideAdmin0Borders: bool = False
	hideAdmin1Borders: bool = True
	hideRivers: bool = True
	hideLakes: bool = True

	class _(JSONWizard.Meta):
		tag = "worldMap"


@dataclass
class PolalGridConfig(JSONWizard):
	class _(JSONWizard.Meta):
		tag = "polarGrid"


@dataclass
class MiscStatsConfig(JSONWizard):
	fontThickness: float = 1.5

	class _(JSONWizard.Meta):
		tag = "miscStats"


@dataclass
class RawMessageConfig(JSONWizard):
	fontThickness: float
	numMessagesToKeep: int

	class _(JSONWizard.Meta):
		tag = "rawMessages"


@dataclass
class SignalChartConfig(JSONWizard):
	"""Configuration for the SNR bar chart"""

	marginLeft: float = 45
	marginRight: float = 10
	marginTop: float = 20
	marginBottom: float = 20

	markerWidth: float = 5
	markerStrokeWidth: float = 1.5

	minValue: float = 0
	maxValue: float = 60
	markerStep: float = 10

	countUntrackedSatellites: bool = False

	class _(JSONWizard.Meta):
		tag = "signalGraph"


@dataclass
class Config(JSONWizard):
	"""Configuration for the app"""

	class _(JSONWizard.Meta):
		tag_key = "type"

	paletteName: str
	multiScreen: bool
	mqttHost: str
	mqttPort: int
	satelliteTTL: int
	windows: list[
		MapConfig | PolalGridConfig | MiscStatsConfig | RawMessageConfig | SignalChartConfig
	]


def loadConfig() -> Config:
	"""Load the configuration from a file"""
	with open("config.json5", "r", encoding="utf8") as f:
		return Config.from_dict(pyjson5.decode(f.read()))
