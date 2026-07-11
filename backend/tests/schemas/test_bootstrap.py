import pytest
from pydantic import ValidationError

from backend.app.schemas.bootstrap import BootstrapSetup


def test_bootstrap_validates_username():
    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="     ",
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            organization_name="Org-name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David Hruby",
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            organization_name="Org-name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    bootstrap = BootstrapSetup(
        username=" David123  ",
        email="hrubyd74@gmail.com",
        password="abcd12345efg",
        organization_name="Org-name",
        team_name="Team-name",
        bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
    )
    assert bootstrap.username == "David123"


def test_bootstrap_validates_password():
    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David123",
            email="hrubyd74@gmail.com",
            password="abcd 1234",
            organization_name="Org-name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David123",
            email="hrubyd74@gmail.com",
            password="abcd1234=",
            organization_name="Org-name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    bootstrap = BootstrapSetup(
        username="David123",
        email="hrubyd74@gmail.com",
        password="Abcd1234!_",
        organization_name="Org-name",
        team_name="Team-name",
        bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
    )
    assert bootstrap.password == "Abcd1234!_"


def test_bootstrap_validates_organization_name_or_team_name():
    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David123",
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            organization_name="Org-name",
            team_name="   ",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David123",
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            organization_name="Org.name",
            team_name="Team-name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    with pytest.raises(ValidationError):
        BootstrapSetup(
            username="David123",
            email="hrubyd74@gmail.com",
            password="abcd12345efg",
            organization_name="Org-name",
            team_name="Team/name",
            bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
        )

    bootstrap = BootstrapSetup(
        username="David123",
        email="hrubyd74@gmail.com",
        password="abcd12345efg",
        organization_name=" Org-name_1: ",
        team_name=" Team name-2_3: ",
        bootstrap_secret="qwertyuiopasdfghjklzxcvbnm1234567890"
    )
    assert bootstrap.organization_name == "Org-name_1:"
    assert bootstrap.team_name == "Team name-2_3:"
