"""JwtSettingsMixin."""
import os


class JwtSettingsMixin:
    """Db settings mixin."""

    public_key_url: str | None = os.environ["PUBLIC_KEY_URL"]
