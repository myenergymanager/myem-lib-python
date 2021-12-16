import os
from typing import Optional


class JwtSettingsMixin:
    """Db settings mixin."""

    public_key_url: Optional["str"] = os.environ["PUBLIC_KEY_URL"]
