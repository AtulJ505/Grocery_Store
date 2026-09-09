import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'JWT_SECRET_KEY': 'test-only-jwt-signing-key-not-for-deployment',
        'MAIL_SUPPRESS_SEND': True,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
