import json

from flask import current_app

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestAuthBluePrint(BaseTestCase):

    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({
                    "username": "justatest",
                    "email": "test@test.com",
                    "password": "12456",
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully registered.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)
    
    def test_user_registration_duplicate_email(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({
                    "username": "foobar",
                    "email": "test@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                "Sorry. That user already exists.", data["message"]
            )
            self.assertIn("fail", data["status"])

    def test_user_registration_duplicate_username(self):
        add_user("test", "test@test.com", "test")
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({
                    "username": "test",
                    "email": "unique_email@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                "Sorry. That user already exists.", data["message"]
            )
            self.assertIn("fail", data["status"])

    def test_user_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps({
                    "username": "user1",
                    "email": "unique_email@test.com",
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                "Invalid payload.", data["message"]
            )
            self.assertIn("fail", data["status"])

    def test_registered_user_login(self):
        with self.client:
            add_user("test", "test@test.com", "test")
            response = self.client.post(
                "/auth/login",
                data=json.dumps({
                    "email": "test@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged in.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")
            self.assertTrue(response.status_code == 200)

    def test_non_registered_user_login(self):
        with self.client:
            response = self.client.post(
                "/auth/login",
                data=json.dumps({
                    "email": "test@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "User does not exist.")
            self.assertTrue(response.content_type == "application/json")
            self.assertTrue(response.status_code == 404)

    def test_valid_logout(self):
        with self.client:
            add_user("test", "test@test.com", "test")
            login_resp = self.client.post(
                "/auth/login",
                data=json.dumps({
                    "email": "test@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            # valid token logout
            token = json.loads(login_resp.data.decode())["auth_token"]
            logout_resp = self.client.get(
                "/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
            data = json.loads(logout_resp.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged out.")
            self.assertEqual(logout_resp.status_code, 200)

    def test_invalid_logout_expired_token(self):
        with self.client:
            add_user("test", "test@test.com", "test")

            # all tokens will be expired
            current_app.config["TOKEN_EXPIRATION_SECONDS"] = -1
            login_resp = self.client.post(
                "/auth/login",
                data=json.dumps({
                    "email": "test@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            token = json.loads(login_resp.data.decode())["auth_token"]
            logout_resp = self.client.get(
                "/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
            data = json.loads(logout_resp.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(
                data["message"] == "Signature Expired. Please log in again."
            )
            self.assertEqual(logout_resp.status_code, 401)
    
    def test_invalid_logout(self):
        with self.client:
            logout_resp = self.client.get(
                "/auth/logout",
                headers={"Authorization": "Bearer NONE"}
            )
            data = json.loads(logout_resp.data.decode())
            x = data["message"]
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(
                data["message"] == "Invalid Token. Please log in again."
            )
            self.assertEqual(logout_resp.status_code, 401)
    
    def test_user_status(self):
        """Test sending auth token in /status"""
        add_user("test", "test@test.com", "test")
        with self.client:
            resp_login = self.client.post(
                "/auth/login",
                data=json.dumps({
                    "email": "test@test.com",
                    "password": "test",
                }),
                content_type="application/json"
            )
            token = json.loads(resp_login.data.decode())["auth_token"]
            response = self.client.get(
                "auth/status",
                headers={"Authorization": f"Bearer {token}"}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["data"] is not None)
            self.assertTrue(data["data"]["username"] == "test")
            self.assertTrue(data["data"]["email"] == "test@test.com")
            self.assertTrue(data["data"]["active"] is True)
            self.assertTrue(response.status_code == 200)
    
    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                "/auth/status",
                headers = {"Authorization": "Bearer NONE"}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(
                data["message"] == "Invalid Token. Please log in again."
            )
            self.assertTrue(response.status_code == 401)