import pytest
from pydantic import ValidationError

from backend.app.schemas.team import TeamCreate, TeamUpdate


@pytest.mark.parametrize("schema", [TeamCreate, TeamUpdate])
def test_team_name_is_stripped(schema):
    team = schema(name="  Team-name_1:  ")

    assert team.name == "Team-name_1:"


@pytest.mark.parametrize("schema", [TeamCreate, TeamUpdate])
@pytest.mark.parametrize("name", ["   ", "Team/name"])
def test_team_name_rejects_blank_or_invalid_characters(schema, name):
    with pytest.raises(ValidationError):
        schema(name=name)


def test_team_update_accepts_explicit_null_name():
    team = TeamUpdate(name=None)

    assert team.name is None
