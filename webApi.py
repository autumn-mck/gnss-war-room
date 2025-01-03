from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def indexRoute():
	return send_file("web/index.html")


@app.route("/style.css")
def styleRoute():
	return send_file("web/style.css")


@app.route("/script.js")
def scriptRoute():
	return send_file("web/script.js")


@app.route("/map")
def mapRoute():
	return send_file("web/map.svg")


@app.route("/polarGrid")
def polarGridRoute():
	return send_file("web/polarGrid.svg")


@app.route("/stats")
def miscStatsRoute():
	return send_file("web/stats.svg")


if __name__ == "__main__":
	app.run()
