from flask import Blueprint, jsonify, request

from project.api.models import User
from project import db

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify({
        "status": "success",
        "message": "pong!",
    })

@users_blueprint.route("/users", methods=["POST"])
def add_user():
    invalid_response = {
        "status": "fail",
        "message": "Invalid payload."
    }
    post_data = request.get_json()
    if not post_data:
        return jsonify(invalid_response), 400

    email = post_data.get("email")
    username = post_data.get("username")

    if email is None or username is None: 
        return jsonify(invalid_response), 400

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        response_object = {
            "status": "fail",
            "message": "Sorry. That email already exists."
        }
        return jsonify(response_object), 400
    
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    response_object = {
        "status": "success",
        "message": f"{email} was added!"
    }
    # 201 response == `created`
    return jsonify(response_object), 201

@users_blueprint.route("/users/<user_id>", methods=["GET"])
def get_single_user(user_id):
    """Get single user details"""

    response_object = {
        "status": "fail",
        "message": "User does not exist"
    }
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify(response_object), 404

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify(response_object), 404

    del response_object["message"]
    response_object.update({
        "status": "success",
        "data": {
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
        }
    })
    return jsonify(response_object), 200

@users_blueprint.route("/users", methods=["GET"])
def get_all_users():
    """Get all users"""
    users = User.query.order_by(User.created_at).all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
        })

    response_object = {
        "status": "success",
        "data": {
            "users": users_list
        },
    }
    return jsonify(response_object), 200