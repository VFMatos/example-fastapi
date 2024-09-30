import jwt
import pytest
from app import schemas
from app import config

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm


# def test_root(client):
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello World"}
#     assert response.json().get("message") == "Hello World"
#     assert response.status_code == 200


def test_create_user(client):
    response = client.post("/users/", json=schemas.UserCreate(email="dummy@gmail.com", password="123").model_dump())

    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "dummy@gmail.com"
    assert response.status_code == 201


def test_login_user(client, test_user):
    response = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})

    login_res = schemas.Token(**response.json())

    payload = jwt.decode(login_res.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    id = payload.get("id")

    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrong_email@gmail.com', '123', 403),
    ('test_user@gmail.com', 'wrong_password', 403),
    ('wrong_email@gmail.com', 'wrong_password', 403),
    (None, '123', 422),
    ('test_user@gmail.com', None, 422)
])
def test_incorrect_login(client, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})

    assert response.status_code == status_code
