from dataclasses import dataclass
import pyjson5
from dataclass_wizard import JSONWizard

@dataclass
class MapConfig(JSONWizard):
	"""Configuration for the map."""
	scaleFactor: float
	scaleMethod: str
	hideKey: bool

	focusLat: float
	focusLong: float

	hideCities: bool
	hideAdmin0Borders: bool
	hideAdmin1Borders: bool
	hideRivers: bool
	hideLakes: bool

	class _(JSONWizard.Meta):
		tag = "worldMap"

@dataclass
class PolalGridConfig(JSONWizard):
	class _(JSONWizard.Meta):
		tag = "polarGrid"

@dataclass
class MiscStatsConfig(JSONWizard):
	class _(JSONWizard.Meta):
		tag = "miscStats"

@dataclass
class RawMessageConfig(JSONWizard):
	fontThickness: float
	numMessagesToKeep: int
	class _(JSONWizard.Meta):
		tag = "rawMessages"

@dataclass
class Config(JSONWizard):
	"""Configuration for the app"""
	class _(JSONWizard.Meta):
		tag_key = "type"

	paletteName: str
	multiScreen: bool
	mqttHost: str
	mqttPort: int
	windows: list[MapConfig | PolalGridConfig | MiscStatsConfig | RawMessageConfig]

def loadConfig() -> Config:
	"""Load the configuration from a file"""
	with open("config.json5", "r", encoding="utf8") as f:
		return Config.from_dict(pyjson5.decode(f.read()))
