from fastapi import HTTPException, status
from typing import Optional


class LinkException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotUniqueAliasError(LinkException):
    """Ошибка при попытке использовать уже занятый alias"""
    def __init__(self, alias: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom alias '{alias}' already exists. Please choose another one."
        )


class AliasLengthError(LinkException):
    """Ошибка при недопустимой длине alias"""
    def __init__(self, alias: str, min_len: int = 5, max_len: int = 15):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Alias '{alias}' must be between {min_len} and {max_len} characters long."
        )


class LinkExpiredError(LinkException):
    """Ошибка при истечении срока действия ссылки"""
    def __init__(self, short_code: str):
        super().__init__(
            status_code=status.HTTP_410_GONE,
            detail=f"Link '{short_code}' has expired and is no longer available."
        )


class PermissionDeniedError(LinkException):
    """Ошибка при отсутствии прав доступа"""
    def __init__(self, action: str = "perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to {action}."
        )


class InvalidURLFormatError(LinkException):
    """Ошибка при невалидном формате URL"""
    def __init__(self, url: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL format: '{url}'. Please provide a valid URL starting with http:// or https://"
        )