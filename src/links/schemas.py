from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional


class LinkBase(BaseModel):
    original_url: HttpUrl = Field(example="https://vkvideo.ru")
    custom_alias: Optional[str] = Field(
        None,
        min_length=4,
        max_length=16,
        pattern="^[a-zA-Z0-9_-]+$",
        example="my-link"
    )
    expire_at: Optional[datetime] = Field(
        example=f"{(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(timespec='minutes')}"
    )

    @field_validator('expire_at')
    def validate_expire_at(cls, value):
        if value and value < datetime.now(value.tzinfo):
            raise ValueError("Expiration date must be in the future")
        return value.replace(second=0, microsecond=0) if value else None


class LinkCreate(LinkBase):
    @field_validator('original_url')
    def ensure_scheme(cls, url):
        if not str(url).startswith(('http://', 'https://')):
            return f"http://{url}"
        return url


class LinkResponse(LinkBase):
    short_id: str = Field(example="abc123")
    created_at: datetime = Field(example=datetime.now(timezone.utc).isoformat())


class LinkStatsResponse(LinkResponse):
    click_count: int = Field(example=42)


class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    expire_at: Optional[datetime] = None

    @field_validator('expire_at')
    def round_expire_at(cls, value):
        return value.replace(second=0, microsecond=0) if value else None