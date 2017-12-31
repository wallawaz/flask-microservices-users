import datetime
import unittest

import json

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase


class TestDevelopmentConfig(BaseTestCase):
    """Tests for the users service"""

    def add_user(self, username, email, created_at=datetime.datetime.utcnow()):
        """helper function to add a user to db"""
        user = User(username=username, email=email, created_at=created_at)
        db.session.add(user)
        db.session.commit()
        return user

    def test_users(self):
        """Ensure /ping works correctly"""
        response = self.client.get("/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn("pong!", data["message"])
        self.assertIn("success", data["status"])

    def test_add_user(self):
        """Ensure a new user can be added to db"""
        # self.client == flask.testing.FlaskClient
        with self.client: 
            response = self.client.post(
                "/users",
                data=json.dumps(dict(
                    username="Ben",
                    email="bwallad@example.com"
                )),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn("bwallad@example.com was added!", data["message"])
            self.assertIn("success", data["status"])

    def test_add_user_invalid_json(self):
        """Ensure Error is thrown with empty JSON """
        # self.client == flask.testing.FlaskClient
        with self.client: 
            response = self.client.post(
                "/users",
                data=json.dumps(dict()),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_invalid_json_keys(self):
        """Ensure Error is thrown if JSON does not have a username key"""
        # self.client == flask.testing.FlaskClient
        with self.client: 
            response = self.client.post(
                "/users",
                data=json.dumps(dict(email="foobar@example.com")),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_duplicate_user(self):
        """Ensure Error is thrown if email already exists."""
        # self.client == flask.testing.FlaskClient

        json_user = json.dumps(dict(
            email="joe@example.com",
            username="joeexample",
        ))
        with self.client: 
            response = self.client.post(
                "/users",
                data=json_user,
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                "/users",
                data=json_user,
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Sorry. That email already exists.", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user(self):
        """Ensure single user behaves correctly."""

        user = self.add_user("bwallad", "bwallad@example.com")
        with self.client:
            response = self.client.get(f"/users/{user.id}")

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue("created_at" in data["data"])
            self.assertIn("bwallad", data["data"]["username"])
            self.assertIn("bwallad@example.com", data["data"]["email"])
            self.assertIn("success", data["status"])

    def test_single_user_incorrect_id(self):
        """Ensure Error is thrown if user is not found"""
        with self.client:
            response = self.client.get("/users/blahBlah")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn("User does not exist", data["message"])
            self.assertIn("fail", data["status"])


    def test_single_user_does_not_exist(self):
        with self.client:
            response = self.client.get("/users/999")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn("User does not exist", data["message"])
            self.assertIn("fail", data["status"])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        user_info = [
            ("bwallad", "bwallad@example.com", -30),
            ("martin", "martinRules@example.com", 0),
        ]
        for username, email, delta in user_info:
            created_at = datetime.datetime.utcnow() + datetime.timedelta(delta)
            self.add_user(username, email, created_at)
            
        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())
            self.assertTrue(response.status_code, 200)

            response_users = data["data"]["users"]
            self.assertIn("success", data["status"])
            self.assertEqual(len(response_users), 2)

            self.assertTrue(response_users[0]["username"] == user_info[1][0])
            self.assertTrue(response_users[0]["email"] == user_info[1][1])
            self.assertIn("created_at", response_users[0])

            self.assertTrue(response_users[1]["username"] == user_info[0][0])
            self.assertTrue(response_users[1]["email"] == user_info[0][1])
            self.assertIn("created_at", response_users[0])