
from sqlalchemy.exc import IntegrityError


from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user

class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_user("justatest", "test@test.com", "password")
        self.assertTrue(user.id)
        self.assertEqual(user.username, "justatest")
        self.assertEqual(user.email, "test@test.com")
        self.assertTrue(user.password)
        self.assertTrue(user.active)
        self.assertTrue(user.created_at)

    def test_add_user_duplicate_username(self):
        user = add_user("justatest", "test@test.com", "password")
        duplicate_user = User(
            username="justatest", 
            email="test2@test.com",
            password="password1",
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        user = add_user("foobar", "test@test.com", "password")
        duplicate_user = User(
            username="baz",
            email="test@test.com",
            password="password1",
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_passwords_are_random(self):
        user_one = add_user("justatest", "test@test.com", "test")
        user_two = add_user("justatest2", "test2@test.com", "test")
        self.assertNotEqual(user_one.password, user_two.password)