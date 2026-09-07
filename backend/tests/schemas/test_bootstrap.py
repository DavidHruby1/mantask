import pytest
from pydantic import ValidationError

from backend.app.schemas.bootstrap import BootstrapSetup


@pytest.mark.parametrize("username", ["     ", "David Hruby"])
def test_bootstrap_rejects_invalid_username(username):
    with pytest.raises(ValidationError):
        BootstrapSetup(
            username=username,
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            organization_name="Org-name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )


def test_bootstrap_strips_username():
    bootstrap = BootstrapSetup(
        username=" David123  ",
        email="hrubyd74@gmail.com",
        password="abcd12345efg",
        organization_name="Org-name",
        team_name="Team-name",
        bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
    )
    assert bootstrap.username == "David123"


@pytest.mark.parametrize("password", ["abcd 1234", "abcd1234\u20ac"])
def test_bootstrap_rejects_invalid_password(password):
    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David123",
            email="hrubyd74@gmail.com",
            password=password,
            organization_name="Org-name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )


def test_bootstrap_accepts_valid_password():
    bootstrap = BootstrapSetup(
        username="David123",
        email="hrubyd74@gmail.com",
        password="Abcd1234=_",
        organization_name="Org-name",
        team_name="Team-name",
        bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
    )
    assert bootstrap.password == "Abcd1234=_"


@pytest.mark.parametrize(
    ("field", "name"),
    [
        ("team_name", "   "),
        ("organization_name", "Org/name"),
        ("team_name", "Team/name"),
    ],
)
def test_bootstrap_rejects_invalid_organization_or_team_name(field, name):
    data = {
        "username": "David123",
        "email": "hrubyd74@gmail.com",
        "password": "abcd12345efg",
        "organization_name": "Org-name",
        "team_name": "Team-name",
        "bootstrap_secret": "qwertyuiopasdfghjklzxcvbnm1234567890",
    }
    data[field] = name

    with pytest.raises(ValidationError):
        BootstrapSetup(**data)


def test_bootstrap_strips_valid_organization_and_team_names():
    bootstrap = BootstrapSetup(
        username="David123",
        email="hrubyd74@gmail.com",
        password="abcd12345efg",
        organization_name=" Mandík, a.s. ",
        team_name=" Team, a.s. ",
        bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
    )
    assert bootstrap.organization_name == "Mandík, a.s."
    assert bootstrap.team_name == "Team, a.s."
