import pytest
from pydantic import ValidationError

from app.api.schemas.query_schema import QuerySchema


def test_query_is_trimmed():
    assert QuerySchema(query="  查询销售额  ").query == "查询销售额"


@pytest.mark.parametrize("value", ["", " ", "a", "x" * 1001])
def test_invalid_query_is_rejected(value: str):
    with pytest.raises(ValidationError):
        QuerySchema(query=value)
