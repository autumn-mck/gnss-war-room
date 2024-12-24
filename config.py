from dataclasses import dataclass
import pyjson5
from dataclass_wizard import JSONWizard
from mapdata.maps import MapConfig, PolalGridConfig

@dataclass
class Config(JSONWizard):
	"""Configuration for the app"""
	class _(JSONWizard.Meta):
		tag_key = "type"

	paletteName: str
	multiScreen: bool
	mqttHost: str
	mqttPort: int
	windows: list[MapConfig | PolalGridConfig]

def loadConfig() -> Config:
	"""Load the configuration from a file"""
	with open("config.json5", "r", encoding="utf8") as f:
		return Config.from_dict(pyjson5.decode(f.read()))
