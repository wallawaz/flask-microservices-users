import datetime
import unittest

import json

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestDevelopmentConfig(BaseTestCase):
    """Tests for the users service"""

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
                    email="bwallad@example.com",
                    password="testpassword",
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
        json_user = json.dumps(dict(
            email="joe@example.com",
            username="joeexample",
            password="testpassword",
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

        user = add_user("bwallad", "bwallad@example.com", "testpassword")
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
            ("bwallad", "bwallad@example.com", "pass1", -30),
            ("martin", "martinRules@example.com", "pass2", 0),
        ]
        for username, email, password, delta in user_info:
            created_at = datetime.datetime.utcnow() + datetime.timedelta(delta)
            add_user(username, email, password, created_at)
            
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
    
    def test_add_user_invalid_json_keys_no_password(self):
        """Ensure an error is thrown if JSON does not have a password key."""
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps(dict(
                    username="ihavenopassword",
                    email="nopass@test.com",
                )),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload.", data["message"])
            self.assertIn("fail", data["status"])
    
    def test_encode_with_auth_token(self):
        user = add_user("justatest", "test@test.com", "test")
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))