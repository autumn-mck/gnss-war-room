from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def index():
	return send_file('web/index.html')

@app.route('/style.css')
def style():
	return send_file('web/style.css')

@app.route('/script.js')
def script():
	return send_file('web/script.js')

@app.route('/map')
def map():
	return send_file('web/map.svg')

if __name__ == '__main__':
	app.run()
