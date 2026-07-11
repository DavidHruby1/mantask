import pytest

from pydantic import ValidationError

from backend.app.schemas.auth import RegisterInput


@pytest.mark.parametrize("username", ["     ", "David Hruby"])
def test_register_rejects_invalid_username(username):
    with pytest.raises(ValidationError):
        RegisterInput(
            username=username,
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            password_confirmation="abcd12345efg"
        )


def test_register_strips_username():
    register = RegisterInput(
        username=" David123  ",
        email="hrubyd74@gmail.com",
        password="abcd12345efg",
        password_confirmation="abcd12345efg"
    )
    assert register.username == "David123"


@pytest.mark.parametrize("password", ["abcd 1234", "abcd1234\u20ac"])
def test_register_rejects_invalid_password(password):
    with pytest.raises(ValidationError):
        RegisterInput(
            username="David123",
            email="hrubyd74@gmail.com",
            password=password,
            password_confirmation=password
        )


def test_register_rejects_mismatched_passwords():
    with pytest.raises(ValidationError):
        RegisterInput(
            username="David123",
            email="hrubyd74@gmail.com",
            password="abcd1234=",
            password_confirmation="abcd1235-"
        )


def test_register_accepts_valid_password():
    register = RegisterInput(
        username="David123",
        email="hrubyd74@gmail.com",
        password="Abcd1234=_",
        password_confirmation="Abcd1234=_"
    )
    assert register.password == "Abcd1234=_"
