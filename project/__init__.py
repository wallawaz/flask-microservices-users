# project/__init__.py

import os
import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# instantiate db
db = SQLAlchemy()
# instantiate flask migrate
migrate = Migrate()

def create_app():
    # instantiate
    app = Flask(__name__)

    # enable CORS
    CORS(app)
    
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    db.init_app(app)
    migrate.init_app(app, db)

    
    from project.api.views import users_blueprint
    app.register_blueprint(users_blueprint)

    return app