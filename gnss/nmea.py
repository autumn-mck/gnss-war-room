from pynmeagps import NMEAMessage
from gnss.satellite import SatelliteInView

def filterMessagesToType(nmeaMessages: list[NMEAMessage], messageType: str) -> list[NMEAMessage]:
	return [
		parsedData for parsedData in nmeaMessages
		if parsedData.msgID == messageType
	]

def parseSatelliteInMessage(parsedData: NMEAMessage) -> list[SatelliteInView]:
	"""Parse a GSV message into a list of SatelliteInView objects"""
	if parsedData.msgID != 'GSV':
		raise ValueError(f"Expected GSV message, got {parsedData.msgID}")

	return [
		SatelliteInView(
			prnNumber=getattr(parsedData, f'svid_0{satNum+1}'),
			network=parsedData.talker,
			elevation=getattr(parsedData, f'elv_0{satNum+1}'),
			azimuth=getattr(parsedData, f'az_0{satNum+1}'),
			snr=getattr(parsedData, f'cno_0{satNum+1}')
		)
		for satNum in range(3)
		if hasattr(parsedData, f'svid_0{satNum+1}')
	]
