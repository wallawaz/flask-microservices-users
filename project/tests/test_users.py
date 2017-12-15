import unittest

import json

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase


class TestDevelopmentConfig(BaseTestCase):
    """Tests for the users service"""

    def add_user(self, username, email):
        """helper function to add a user to db"""
        user = User(username=username, email=email)
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
            ("bwallad", "bwallad@example.com"),
            ("martin", "martinRules@example.com"),
        ]
        for username, email in user_info:
            self.add_user(username, email)

        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())
            self.assertTrue(response.status_code, 200)

            response_users = data["data"]["users"]
            response_users.sort(key=lambda x: x["created_at"])
            self.assertEqual(len(response_users), 2)

            for i, user in enumerate(user_info):
                response_user = response_users[i]
                self.assertTrue("created_at" in response_user)
                self.assertTrue(response_user["username"] == user[0])
                self.assertTrue(response_user["email"] == user[1])
            self.assertIn("success", data["status"])

    def test_index_no_users(self):
        """Ensure the route behaves correctly when no users have been added to db"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<h1>All Users</h1>", response.data)
        self.assertIn(b"<p>No users!</p>", response.data)
    
    def test_index_with_users(self):
        self.add_user("bwallad", "bwallad@example.com")
        self.add_user("carebear", "sharingIsCaring@gmail.com")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<h1>All Users</h1>", response.data)
        self.assertNotIn(b"<strong>bwallad<strong>", response.data)
        self.assertNotIn(b"<strong>carebear<strong>", response.data)
    
    def test_index_add_user(self):
        """Ensure a new user can be added to the db"""
        with self.client:
            response = self.client.post(
                "/",
                data=dict(username="bwallad", email="bwallad@example.com"),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<h1>All Users</h1>', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'<strong>bwallad</strong>', response.data)