"""Common config mixins."""
import os
from typing import Optional


class DbSettingsMixin:
    """Db settings mixin."""

    db_host: Optional["str"] = os.getenv("DB_HOST")
    db_user: Optional["str"] = os.getenv("DB_USER")
    db_password: Optional["str"] = os.getenv("DB_PASSWORD")
    db_name: Optional["str"] = os.getenv("DB_NAME")


class JwtSettingsMixin:
    """Db settings mixin."""

    public_key_url: Optional["str"] = os.getenv("PUBLIC_KEY_URL")
