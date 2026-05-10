import pytest

from datetime import datetime, timedelta, timezone
from pydantic import ValidationError

from src.links.schemas import LinkCreate

EXPIRE_AT = "2027-04-30T22:30+00:00"

def test_expire_at_in_past():
    past_date = datetime.now(timezone.utc) - timedelta(days=1)

    with pytest.raises(ValidationError) as exc:
        LinkCreate(
            original_url="https://example.com",
            custom_alias="test",
            expire_at=past_date,
        )

    assert "Expiration date must be in the future" in str(exc.value)


def test_original_url_without_scheme():
    data = LinkCreate(
        original_url="google.com",
        custom_alias="google",
        expire_at=EXPIRE_AT
    )
    print(str(data.original_url))
    assert str(data.original_url).startswith("http://")
    assert str(data.original_url) == "http://google.com/"


def test_original_url_with_https_scheme():
    data = LinkCreate(
        original_url="https://github.com",
        custom_alias="github",
        expire_at=EXPIRE_AT
    )

    assert str(data.original_url) == "https://github.com/"


def test_original_url_with_http_scheme():
    data = LinkCreate(
        original_url="http://example.com",
        custom_alias="example",
        expire_at=EXPIRE_AT
    )

    assert str(data.original_url) == "http://example.com/"