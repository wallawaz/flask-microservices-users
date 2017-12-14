# project/__init__.py

import os
from flask import Flask, jsonify

# instantiate
app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS")
app.config.from_object(app_settings)

#print(app.config)
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify({
        "status": "success",
        "message": "pong!",
    })
