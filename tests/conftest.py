import pytest
from app import create_app
from models import MediaLibrary


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    # Replace the library loaded from disk with a fresh one for each test.
    app.library = MediaLibrary()
    return app


@pytest.fixture
def client(app):
    return app.test_client()
