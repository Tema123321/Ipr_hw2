from src.links.exceptions import (
    NotUniqueAliasError,
    AliasLengthError,
    LinkExpiredError,
    PermissionDeniedError,
    InvalidURLFormatError,
)


def test_not_unique_alias_error():
    exc = NotUniqueAliasError("alias")

    assert exc.status_code == 400
    assert "already exists" in exc.detail



def test_alias_length_error():
    exc = AliasLengthError("abc")

    assert exc.status_code == 400
    assert "must be between" in exc.detail



def test_link_expired_error():
    exc = LinkExpiredError("expired")

    assert exc.status_code == 410



def test_permission_denied_error():
    exc = PermissionDeniedError()

    assert exc.status_code == 403



def test_invalid_url_format_error():
    exc = InvalidURLFormatError("bad-url")

    assert exc.status_code == 400
    assert "Invalid URL format" in exc.detail