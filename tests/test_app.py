import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Hello World" in rv.data


def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.is_json
    assert rv.get_json() == {"status": "healthy"}
