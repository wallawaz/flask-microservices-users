import unittest

import json

from project.tests.base import BaseTestCase


class TestDevelopmentConfig(BaseTestCase):
    """Tests for the users service"""

    def test_users(self):
        """Ensure /ping works correctly"""
        response = self.client.get("/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn("pong!", data["message"])
        self.assertIn("success", data["status"])
