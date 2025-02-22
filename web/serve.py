from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def indexRoute():
	return send_file("index.html")


@app.route("/style.css")
def styleRoute():
	return send_file("style.css")


@app.route("/script.js")
def scriptRoute():
	return send_file("../dist/script.js")


@app.route("/favicon.ico")
def faviconRoute():
	return send_file("favicon.ico")


@app.route("/robots.txt")
def robotsRoute():
	return send_file("robots.txt")


@app.route("/map")
def mapRoute():
	return send_file("generated/map.svg")


@app.route("/polarGrid")
def polarGridRoute():
	return send_file("generated/polarGrid.svg")


@app.route("/stats")
def miscStatsRoute():
	return send_file("generated/stats.svg")


@app.route("/snr-chart")
def snrChartRoute():
	return send_file("generated/snrChart.svg")


@app.route("/api/gnss")
def satellitesRoute():
	return send_file("generated/gnssData.json")


@app.route("/continents.geojson")
def continentsRoute():
	return send_file("generated/continents.geojson")


@app.route("/borders.geojson")
def bordersRoute():
	return send_file("generated/borders.geojson")


@app.route("/palette.json")
def paletteRoute():
	return send_file("generated/palette.json")


if __name__ == "__main__":
	app.run()
