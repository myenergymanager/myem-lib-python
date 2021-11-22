import pytest
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey
from myem_lib.exceptions import BadRequest, Unauthenticated
from myem_lib.utils import TokenDecoder


class TestTokenDecoder:
    def test_decode_jwt_token(self, generate_token):
        assert TokenDecoder.decode_jwt_token(url="", token=generate_token).keys().__contains__("id")

    def test_decode_when_not_bearer_token(self, generate_token):
        with pytest.raises(BadRequest):
            TokenDecoder.decode_jwt_token(url="", token="KEY" + generate_token.split()[1])

    def test_decode_jwt_token_invalid_token(self, generate_token):
        with pytest.raises(BadRequest):
            TokenDecoder.decode_jwt_token(url="", token=generate_token.split()[1])

    def test_get_public_key_when_not_authorized(self):
        with pytest.raises(Unauthenticated):
            TokenDecoder.get_public_key(url="", token="")

    def test_get_public_key(self):
        url = "https://dev-87evx9ru.auth0.com/.well-known/jwks.json"
        token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5FRTFRVVJCT1RNNE16STVSa0ZETlRZeE9U"
            "VTFNRGcyT0Rnd1EwVXpNVGsxUWpZeVJrUkZRdyJ9.eyJpc3MiOiJodHRwczovL2Rldi04N2V2eDlydS5"
            "hdXRoMC5jb20vIiwic3ViIjoiYVc0Q2NhNzl4UmVMV1V6MGFFMkg2a0QwTzNjWEJWdENAY2xpZW50cyI"
            "sImF1ZCI6Imh0dHBzOi8vZXhwZW5zZXMtYXBpIiwiaWF0IjoxNTcyMDA2OTU0LCJleHAiOjE1NzIwMDY"
            "5NjQsImF6cCI6ImFXNENjYTc5eFJlTFdVejBhRTJINmtEME8zY1hCVnRDIiwiZ3R5IjoiY2xpZW50LWN"
            "yZWRlbnRpYWxzIn0.PUxE7xn52aTCohGiWoSdMBZGiYAHwE5FYie0Y1qUT68IHSTXwXVd6hn02HTah6e"
            "pvHHVKA2FqcFZ4GGv5VTHEvYpeggiiZMgbxFrmTEY0csL6VNkX1eaJGcuehwQCRBKRLL3zKmA5IKGy5G"
            "eUnIbpPHLHDxr-GXvgFzsdsyWlVQvPX2xjeaQ217r2PtxDeqjlf66UYl6oY6AqNS8DH3iryCvIfCcybR"
            "Zkc_hdy-6ZMoKT6Piijvk_aXdm7-QQqKJFHLuEqrVSOuBqqiNfVrG27QzAPuPOxvfXTVLXL2jek5meH"
            "6n-VWgrBdoMFH93QEszEDowDAEhQPHVs0xj7SIzA"
        )
        assert isinstance(TokenDecoder.get_public_key(url=url, token=token), _RSAPublicKey)
