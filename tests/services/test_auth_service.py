import pytest
from app.services.auth import hash_password, check_password, _encode_jwt, decode_jwt, generate_access_token
from app.exceptions.user import UserNotFound, IncorrectPassword
from app.models.user import User, UserRole

def test_hash_and_check_ok():
    hp = hash_password("abc")
    assert isinstance(hp, str) and hp != "abc"
    assert check_password("abc", hp) is True

def test_check_bad_password():
    hp = hash_password("abc")
    assert check_password("zzz", hp) is False

def test_check_invalid_hash():
    with pytest.raises(ValueError):
        check_password("abc", "bad-format")

def test_encode_decode_jwt_roundtrip():
    token = _encode_jwt("user-id-123")
    data = decode_jwt(token)
    assert data["user_id"] == "user-id-123"

def test_generate_access_token_ok(db_session):
    u = User(first_name="A", last_name="B", email="a@b.c", role=UserRole.student, hashed_password=hash_password("pw"))
    db_session.add(u); db_session.commit()
    token = generate_access_token(db_session, "a@b.c", "pw")
    assert isinstance(token, str)

def test_generate_access_token_user_not_found(db_session):
    with pytest.raises(UserNotFound):
        generate_access_token(db_session, "no@no.no", "pw")

def test_generate_access_token_bad_password(db_session):
    u = User(first_name="A", last_name="B", email="x@y.z", role=UserRole.student, hashed_password=hash_password("pw"))
    db_session.add(u); db_session.commit()
    with pytest.raises(IncorrectPassword):
        generate_access_token(db_session, "x@y.z", "wrong")
