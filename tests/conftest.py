import pytest

@pytest.fixture(scope='session')
def setup_database():
    from app import db
    db.create_all()
    yield
    db.drop_all()