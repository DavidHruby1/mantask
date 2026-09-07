import pytest
from pydantic import ValidationError

from backend.app.schemas.team import TeamCreate, TeamUpdate


@pytest.mark.parametrize("schema", [TeamCreate, TeamUpdate])
def test_team_name_is_stripped(schema):
    team = schema(name="  Mandík, a.s.  ")

    assert team.name == "Mandík, a.s."


@pytest.mark.parametrize("schema", [TeamCreate, TeamUpdate])
@pytest.mark.parametrize("name", ["   ", "Team/name"])
def test_team_name_rejects_blank_or_invalid_characters(schema, name):
    with pytest.raises(ValidationError):
        schema(name=name)


def test_team_update_accepts_explicit_null_name():
    team = TeamUpdate(name=None)

    assert team.name is None
