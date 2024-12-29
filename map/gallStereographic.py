import math

def latLongToGallStereographic(lat: float, long: float, mapWidth: float) -> tuple[float, float]:
	"""Convert latitude and longitude to Gall Stereographic coordinates."""
	longOffset = -10
	long += longOffset

	# "bounce" off the top when wrapping over the poles
	if lat > 90:
		lat = 180 - lat
		long += 180
	elif lat < -90:
		lat = -180 - lat
		long += 180

	# wrap around the world as the map is not centered at 0
	if long < -180 - longOffset:
		long += 360
	elif long > 180 - longOffset:
		long -= 360

	radius = mapWidth / (2 * math.pi)
	latRad = math.radians(lat)
	longRad = math.radians(long)

	x = radius * longRad # the formula should divide by sqrt(2) here but for some reason that gives the wrong result
	y = -radius * (math.sqrt(2) + 1) * math.tan(latRad / 2)

	return (x, y)