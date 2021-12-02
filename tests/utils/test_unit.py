import os

import pytest
from fastapi.exceptions import HTTPException
from myem_lib.utils import get_active_user, get_private_key, get_public_key


class TestTokenDecoder:
    # we disabled mypy error in this line because the token used for this test is too long.
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InNpZ25rZXkifQ.eyJkZWxldGlvbl9yZXF1ZXN0ZWRfYXQiOiIxODAwLTAxLTAxVDAwOjAwOjAwKzAwOjAwIiwiZW1haWwiOiJmb3VhZCtwYXJlbnRwYXJ0aWN1bGllckBteWVtLmZyIiwiZmlyc3RuYW1lIjoiRm91YWQiLCJpZCI6MjQsImxhc3RfYWN0aW9uX2F0IjoiMjAyMS0xMS0xNVQxNTowNDowNSswMDowMCIsImxhc3RuYW1lIjoiQ0hFTk5PVUYgcGFyZW50IiwicGhvbmUiOiIiLCJ0eXBlIjoxfQ.W7BmD3c2QIBsVTBtrIH5KtEa7Q6xTF24cB4kxy8Qi4N2kD5VBncS5RI3wKsY4Ke_-7BK7pbd0iXhldOh2wQBN7j1Are73-GPbg8BRTxBs_bQ882eAKGhKefkMKodLxBJCpPjhqS5iWmLfDzaP0lyL-7HsYTR0F9Z6AX7sZ8dud4ywbHp-UnvYjDizJGMDTaHp-XEV7n6pfoqQhepcB9lRJtk4jr-jKKDMBYQvP_byZlM0QWCJ0qJFubI4qkNik8W5s5ZQjLzNEogi3Zy3UTQsgy6QKIoukc0zP0JqgmQgrzSWWszmLHxptr4QfceeQCb5Ao8hJxhWFUSH-6nttW_ZvH0Pfh2cD2vKtlf044TlGJtZRj6bmuWbjSWJVTOLF2CRPQ3OQPBhxc_hqmHhGwPtS3oqWMPWcPVkhjoTFbjAz_kRlZiwgj2G_2DdZe01_eKBZrTBvcmWjOwuiU3Yj0YSJSwZhyKJ-vr5bll2qyPCX3FlfclfCeAcYE2jhXaLl3bqoIACqTCMmeZ9W5PVmW7GgVBK1gz6R9jAVs-cov0xBglcI8P_jxsLvmeDQib2OYeimtExFC-71ZlkxjAafafvWh49W6rnSR-u__M9THoDMu5b2VP4G6N84S2d62aIlLRVCP--4lEADCwah8Mtpf__iK5FSCedJ4AAoCrmEKKIdg"  # pylint: disable=C0301

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

    def test_get_public_key_with_staging_url(self):
        key = os.environ["PUBLIC_KEY_URL"]
        os.environ["PUBLIC_KEY_URL"] = os.environ["STAGING_PUBLIC_KEY_URL"]
        assert "BEGIN PUBLIC KEY" in str(get_public_key())
        os.environ["PUBLIC_KEY_URL"] = key

    def test_get_active_user(self, user_token):
        assert "id" in get_active_user(token=user_token["token"])

    def test_decode_token_with_staging_url(self):
        key = os.environ["PUBLIC_KEY_URL"]
        os.environ["PUBLIC_KEY_URL"] = os.environ["STAGING_PUBLIC_KEY_URL"]
        assert "id" in get_active_user(token=self.token)
        os.environ["PUBLIC_KEY_URL"] = key

    def test_get_active_user_with_different_key(self, user_token):
        token = user_token["token"]
        key = os.environ["PUBLIC_KEY_URL"]
        os.environ["PUBLIC_KEY_URL"] = os.environ["STAGING_PUBLIC_KEY_URL"]
        with pytest.raises(HTTPException):
            assert "id" in get_active_user(token=token)
        os.environ["PUBLIC_KEY_URL"] = key
