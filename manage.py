import coverage
import unittest

from flask_script import Manager
from project import create_app, db
from project.api.models import User


COV = coverage.coverage(
    branch=True,
    include="project/*",
    omit=[
        "project/tests/*"
    ],
)
COV.start()

app = create_app()
manager = Manager(app)

@manager.command
def test():
    """Runs the tests without code coverage"""
    loader = unittest.TestLoader()
    tests = loader.discover("project/tests", pattern="test*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def cov():
    """Runs the unit tests with coverage"""
    tests = unittest.TestLoader().discover("project/tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1

@manager.command
def recreate_db():
    """Recreates a database"""
    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.command
def seed_db():
    """Seed the db"""
    db.session.add(User(username="bwallad", email="bwallad@example.com"))
    db.session.add(User(username="martinRules", email="mrules@example.com"))
    db.session.commit()


if __name__ == "__main__":
    manager.run()
