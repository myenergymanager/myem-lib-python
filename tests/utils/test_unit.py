import os

import pytest
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey
from myem_lib.exceptions import Unauthenticated, Unauthorized
from myem_lib.pytest_fixtures import generate_token
from myem_lib.utils import get_active_user, get_public_key


class TestTokenDecoder:
    # we disabled mypy error in this line because the token used for this test is too long.
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InNpZ25rZXkifQ.eyJkZWxldGlvbl9yZXF1ZXN0ZWRfYXQiOiIxODAwLTAxLTAxVDAwOjAwOjAwKzAwOjAwIiwiZW1haWwiOiJmb3VhZCtwYXJlbnRwYXJ0aWN1bGllckBteWVtLmZyIiwiZmlyc3RuYW1lIjoiRm91YWQiLCJpZCI6MjQsImxhc3RfYWN0aW9uX2F0IjoiMjAyMS0xMS0xNVQxNTowNDowNSswMDowMCIsImxhc3RuYW1lIjoiQ0hFTk5PVUYgcGFyZW50IiwicGhvbmUiOiIiLCJ0eXBlIjoxfQ.W7BmD3c2QIBsVTBtrIH5KtEa7Q6xTF24cB4kxy8Qi4N2kD5VBncS5RI3wKsY4Ke_-7BK7pbd0iXhldOh2wQBN7j1Are73-GPbg8BRTxBs_bQ882eAKGhKefkMKodLxBJCpPjhqS5iWmLfDzaP0lyL-7HsYTR0F9Z6AX7sZ8dud4ywbHp-UnvYjDizJGMDTaHp-XEV7n6pfoqQhepcB9lRJtk4jr-jKKDMBYQvP_byZlM0QWCJ0qJFubI4qkNik8W5s5ZQjLzNEogi3Zy3UTQsgy6QKIoukc0zP0JqgmQgrzSWWszmLHxptr4QfceeQCb5Ao8hJxhWFUSH-6nttW_ZvH0Pfh2cD2vKtlf044TlGJtZRj6bmuWbjSWJVTOLF2CRPQ3OQPBhxc_hqmHhGwPtS3oqWMPWcPVkhjoTFbjAz_kRlZiwgj2G_2DdZe01_eKBZrTBvcmWjOwuiU3Yj0YSJSwZhyKJ-vr5bll2qyPCX3FlfclfCeAcYE2jhXaLl3bqoIACqTCMmeZ9W5PVmW7GgVBK1gz6R9jAVs-cov0xBglcI8P_jxsLvmeDQib2OYeimtExFC-71ZlkxjAafafvWh49W6rnSR-u__M9THoDMu5b2VP4G6N84S2d62aIlLRVCP--4lEADCwah8Mtpf__iK5FSCedJ4AAoCrmEKKIdg"  # pylint: disable=C0301
    url = "https://webservice.staging.telso.myem.fr/ng-api/authentication/public_key.json"

    def test_decode_when_not_bearer_token(self):
        with pytest.raises(Unauthorized):
            get_active_user(token="KEY" + generate_token())

    def test_decode_when_not_authorized(self):
        # we disabled mypy error in this line because the token used for this test is too long.
        token = "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5FRTFRVVJCT1RNNE16STVSa0ZETlRZeE9UVTFNRGcyT0Rnd1EwVXpNVGsxUWpZeVJrUkZRdyJ9.eyJpc3MiOiJodHRwczovL2Rldi04N2V2eDlydS5hdXRoMC5jb20vIiwic3ViIjoiYVc0Q2NhNzl4UmVMV1V6MGFFMkg2a0QwTzNjWEJWdENAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vZXhwZW5zZXMtYXBpIiwiaWF0IjoxNTcyMDA2OTU0LCJleHAiOjE1NzIwMDY5NjQsImF6cCI6ImFXNENjYTc5eFJlTFdVejBhRTJINmtEME8zY1hCVnRDIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.PUxE7xn52aTCohGiWoSdMBZGiYAHwE5FYie0Y1qUT68IHSTXwXVd6hn02HTah6epvHHVKA2FqcFZ4GGv5VTHEvYpeggiiZMgbxFrmTEY0csL6VNkX1eaJGcuehwQCRBKRLL3zKmA5IKGy5GeUnIbpPHLHDxr-GXvgFzsdsyWlVQvPX2xjeaQ217r2PtxDeqjlf66UYl6oY6AqNS8DH3iryCvIfCcybRZkc_hdy-6ZMoKT6Piijvk_aXdm7-QQqKJFHLuEqrVSOuBqqiNfVrG27QzAPuPOxvfXTVLXL2jek5meH6n-VWgrBdoMFH93QEszEDowDAEhQPHVs0xj7SIzA"  # pylint: disable=C0301
        os.environ["PUBLIC_KEY_URL"] = self.url
        with pytest.raises(Unauthorized):
            get_active_user(token=token)

    def test_decode_jwt_token_invalid_token(self):
        with pytest.raises(Unauthorized):
            get_active_user(token=generate_token())

    def test_get_public_key_when_not_authenticated(self):
        with pytest.raises(Unauthenticated):
            get_public_key(token="")

    def test_get_public_key(self):
        os.environ["PUBLIC_KEY_URL"] = self.url
        assert isinstance(get_public_key(token=self.token), _RSAPublicKey)
