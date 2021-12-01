"""Common config mixins."""
import os
from typing import Optional


class DbSettingsMixin:
    """Db settings mixin."""

    db_uri: str = (
        f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
    )


class JwtSettingsMixin:
    """Db settings mixin."""

    public_key_url: Optional["str"] = os.environ["PUBLIC_KEY_URL"]
