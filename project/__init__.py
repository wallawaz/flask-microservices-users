# project/__init__.py

import os
import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# instantiate db
db = SQLAlchemy()
# instantiate flask migrate
migrate = Migrate()
# instantiate bcrypt
bcrypt = Bcrypt()


def create_app():
    # instantiate
    app = Flask(__name__)

    # enable CORS
    CORS(app)
    
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    
    from project.api.users import users_blueprint
    from project.api.auth import auth_blueprint
    
    app.register_blueprint(users_blueprint)
    app.register_blueprint(auth_blueprint)

    return app