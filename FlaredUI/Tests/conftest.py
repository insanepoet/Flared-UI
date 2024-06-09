import pytest

from FlaredUI.Modules.DB import db


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope='session', autouse=True)
def init_db():
     with app.app_context():
         db.create_all()
         yield db
         db.drop_all()
