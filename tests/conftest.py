import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.main import app
from app import database, models, schemas, oauth2

SQLALCHEMY_DATABASE_URL = f'sqlite:///./fastapi_test.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

client = TestClient(app)


@pytest.fixture
def session():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    # command.downgrade(revision="base") NOK
    # command.upgrade(revision="head") NOK

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    test_user = schemas.UserCreate(email="test_user@gmail.com", password="test_user_pw")
    response = client.post("/users/", json=test_user.model_dump())

    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = test_user.password

    return new_user


@pytest.fixture
def test_user2(client):
    test_user = schemas.UserCreate(email="test_user2@gmail.com", password="test_user2_pw")
    response = client.post("/users/", json=test_user.model_dump())

    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = test_user.password

    return new_user


@pytest.fixture
def token(test_user):
    return oauth2.create_access_token(data=schemas.TokenData(id=test_user["id"]).model_dump())


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_posts(session, test_user, test_user2):
    post_data = [
        models.Post(owner_id=test_user["id"], title="1st title", content="1st content"),
        models.Post(owner_id=test_user["id"], title="2nd title", content="2nd content"),
        models.Post(owner_id=test_user["id"], title="3rd title", content="3rd content"),
        models.Post(owner_id=test_user2["id"], title="4th title", content="4th content")
    ]

    session.add_all(post_data)
    session.commit()

    posts = session.query(models.Post).all()
    return posts
