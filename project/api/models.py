from datetime import datetime, timedelta
import jwt

from flask import current_app
from project import db, bcrypt


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, server_default="false", nullable=False)
    admin = db.Column(db.Boolean, default=False, server_default="false", nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(
            self, username, email, password,
            created_at=datetime.utcnow()):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password,
            current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.created_at = created_at
    
    def encode_auth_token(self, user_id):
        """Generates the auth token"""
        expire_delta = timedelta(
            days=current_app.config.get("TOKEN_EXPIRATION_DAYS"),
            seconds=current_app.config.get("TOKEN_EXPIRATION_SECONDS"),
        )

        try:
            payload = {
                "exp": datetime.utcnow() + expire_delta,
                "iat": datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(
                payload,
                current_app.config.get("SECRET_KEY"),
                algorithm="HS256",
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_auth_token(auth_token):
        """Decodes the auth_token
        param: auth_token
        return: string|int
        """
        try:
            payload = jwt.decode(
                auth_token,
                current_app.config.get("SECRET_KEY")
            )
            return payload["sub"]
        except jwt.ExpiredSignature:
            return "Signature Expired. Please log in again."
        except jwt.InvalidTokenError:
            return "Invalid Token. Please log in again."