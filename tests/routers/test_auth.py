from unittest.mock import patch
from app.exceptions.user import UserNotFound, IncorrectPassword

def test_get_access_token_success(client):
    mock_token = "mock_jwt_token_abc123"
    with patch("app.routers.auth.generate_access_token", return_value=mock_token) as mock_gen:
        r = client.post("/auth/token", json={"email":"x@y.z","password":"p"})
        assert r.status_code == 200
        assert r.json()["access_token"] == mock_token
        mock_gen.assert_called_once()

def test_get_access_token_user_not_found(client):
    with patch("app.routers.auth.generate_access_token", side_effect=UserNotFound("User not found")):
        r = client.post("/auth/token", json={"email":"none@x.z","password":"p"})
        assert r.status_code == 404
        assert r.json() == {"detail":"User not found"}

def test_get_access_token_incorrect_password(client):
    with patch("app.routers.auth.generate_access_token", side_effect=IncorrectPassword("Incorrect password")):
        r = client.post("/auth/token", json={"email":"x@y.z","password":"bad"})
        assert r.status_code == 400
        assert r.json() == {"detail":"Incorrect password"}

def test_get_access_token_validation_errors(client):
    assert client.post("/auth/token", json={"password":"p"}).status_code == 422
    assert client.post("/auth/token", json={"email":"x@y.z"}).status_code == 422
