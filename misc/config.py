import os
from dataclasses import dataclass, field

import pyjson5
from dataclass_wizard import JSONWizard


@dataclass
class MapConfig(JSONWizard):
	"""Configuration for the map."""

	scaleFactor: float = 1
	scaleMethod: str = "fit"
	hideKey: bool = False
	hideSatelliteTrails: bool = True

	focusLat: float = 0
	focusLong: float = 10

	hideCities: bool = True
	hideAdmin0Borders: bool = False

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
	fontThickness: float = 1.5
	numMessagesToKeep: int = 50

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
class GlobeConfig(JSONWizard):
	class _(JSONWizard.Meta):
		tag = "globe"


@dataclass
class MqttConfig(JSONWizard):
	host: str = "localhost"
	port: int = 1883


@dataclass
class GnssConfig(JSONWizard):
	serialPort: str = "/dev/ttyUSB0"
	baudRate: int = 38400


@dataclass
class Config(JSONWizard):
	"""Configuration for the app"""

	class _(JSONWizard.Meta):
		tag_key = "type"

	paletteName: str = "warGames"
	mqtt: MqttConfig = field(default_factory=MqttConfig)
	multiTrackBroadcasting: list[MqttConfig] = field(default_factory=list)
	gnss: GnssConfig = field(default_factory=GnssConfig)
	satelliteTTL: int = 3600
	warRoom: bool = False
	startupSequence: bool = False
	windows: list[
		MapConfig
		| PolalGridConfig
		| MiscStatsConfig
		| RawMessageConfig
		| SignalChartConfig
		| GlobeConfig
	] = field(
		default_factory=lambda: [
			MapConfig(),
			PolalGridConfig(),
			MiscStatsConfig(),
			RawMessageConfig(),
			SignalChartConfig(),
		]
	)


def loadConfig() -> Config:
	"""Load the configuration from a file"""
	configFile = os.getenv("GNSS_CONFIG_FILE") or "config.json5"

	try:
		with open(configFile, "r", encoding="utf8") as f:
			config = Config.from_dict(pyjson5.decode(f.read()))
	except OSError:
		print("Warning: Failed to read config file, continuing with defaults...")
		config = Config()

	if len(config.windows) == 0:
		config.windows = [MiscStatsConfig()]
	return config
