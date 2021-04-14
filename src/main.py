import os
import threading
from bot import HomeBot
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

bot = HomeBot()
collection = threading.Thread(target=bot.collect_whos_home)
collection.start()

@app.before_request
def check_token():
    token = request.headers.get('Authorization')
    if token != os.environ.get('TOKEN'):
        return 'Invalid Authorization Token'

@app.route('/whoshome', methods=["GET"])
def whos_home():
    seconds = int(request.args.get('seconds', 60))
    return bot.get_whos_home(seconds)

@app.route('/timeseries/<name>', methods=["GET"])
def timeseries(name):
    seconds = int(request.args.get('seconds', 3600))
    return bot.get_timeseries(name, seconds)

app.run(host="192.168.1.7", port=5000, threaded=True)