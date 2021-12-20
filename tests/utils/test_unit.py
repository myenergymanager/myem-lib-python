import pytest
from fastapi.exceptions import HTTPException
from myem_lib.utils import get_active_user, get_active_installer, get_private_key, get_public_key
from uuid import UUID


class TestTokenDecoder:
    def test_get_public_key(self):
        assert "BEGIN PUBLIC KEY" in str(get_public_key())

    def test_get_private_key(self):
        assert "BEGIN PRIVATE KEY" in str(get_private_key())

    def test_decode_when_not_authorized(self):
        with pytest.raises(HTTPException):
            get_active_user(token="")

    def test_decode_jwt_token_invalid_token(self, user_token):
        with pytest.raises(HTTPException):
            get_active_user(token=user_token["token"] + "kdkdkd")

    def test_get_active_user(self, user_token):
        assert "id" in get_active_user(token=user_token["token"])

    def test_get_active_user_with_different_key(self, user_token, user_token_2):
        with pytest.raises(HTTPException):
            assert "id" in get_active_user(token=user_token["token"], index=1)

    def test_get_installer_uuid(self, installer_token):
        assert isinstance(get_active_installer(token=installer_token["token"])['id'], UUID)
