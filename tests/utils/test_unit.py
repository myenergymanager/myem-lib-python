import json
import os
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from myem_lib.db_settings_mixins import DbSettingsMixin
from myem_lib.jwt_settings_mixins import JwtSettingsMixin
from myem_lib.utils import (
    add_validation_exception_handler,
    get_active_user,
    get_private_key,
    get_public_key,
    init_app,
)


@pytest.fixture
def create_exceptions_endpoints(created_app):
    add_validation_exception_handler(created_app)

    class SimpleModel(BaseModel):
        id: int
        dummy: str

    class NestedModel(BaseModel):
        id: int
        nested: SimpleModel

    @created_app.get("/test-exception-response")
    async def exception_response():
        raise HTTPException(detail="raise exception test", status_code=404)

    @created_app.post("/test-validation-error", response_model=SimpleModel)
    async def validation_exception(simple_model: SimpleModel):
        return simple_model

    @created_app.post("/test-nested-validation-error", response_model=NestedModel)
    async def nested_validation_exception(nested_model: NestedModel):
        return nested_model


@pytest.fixture(scope="function")
def mock_public_key():
    public_key = os.environ["PUBLIC_KEY_URL"]
    os.environ["PUBLIC_KEY_URL"] = "wrong key"
    yield
    os.environ["PUBLIC_KEY_URL"] = public_key


class TestTokenDecoder:
    def test_init_app(self, created_app):
        init_app(created_app)

    @pytest.mark.asyncio
    async def test_handle_exception(self, create_exceptions_endpoints, client):
        response = await client.get("/test-exception-response")
        assert response.status_code == 404
        assert response.json() == {"detail": "raise exception test"}
        response = await client.post("/test-validation-error", data=json.dumps({"id": 1}))
        assert response.status_code == 422
        assert response.json() == {"errors": [{"dummy": "field required"}]}
        response = await client.post(
            "/test-nested-validation-error", data=json.dumps({"id": 1, "nested": {"id": 2}})
        )
        assert response.status_code == 422
        assert response.json() == {"errors": [{"nested": ["dummy field required"]}]}

    def test_public_key_bad_format(self, mock_public_key):
        with pytest.raises(HTTPException):
            get_public_key()

    def test_private_key_bad_format(self, mock_public_key):
        with pytest.raises(HTTPException):
            get_private_key()

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

    def test_decode_fast_api_jwt_token(self):
        token = {
            "token": jwt.encode(
                {"id": str(uuid4()), "aud": ["fastapi-users:auth"]},
                get_private_key(),
                algorithm="RS256",
            ),
            "public_key": get_public_key(),
            "private_key": get_private_key(),
        }
        assert "id" in get_active_user(token=token["token"])

    def test_decode_fast_api_jwt_token_with_wrong_audience(self):
        token = {
            "token": jwt.encode(
                {"id": str(uuid4()), "aud": ["test"]}, get_private_key(), algorithm="RS256"
            ),
            "public_key": get_public_key(),
            "private_key": get_private_key(),
        }
        with pytest.raises(HTTPException):
            get_active_user(token=token["token"])

    def test_get_active_user_with_different_key(self, user_token, user_token_2):
        with pytest.raises(HTTPException):
            assert "id" in get_active_user(token=user_token["token"], index=1)

    def test_get_installer_uuid(self, ng_user_token):
        assert UUID(get_active_user(token=ng_user_token["token"])["id"], version=4)


class TestMixins:
    def test_jwt_mixins(self):
        assert JwtSettingsMixin.public_key_url == "https://jsonkeeper.com/b/FXT7"

    def test_db_mixins(self):
        assert (
            DbSettingsMixin.db_uri
            == "postgresql+psycopg2://user_test:password_test@host_test/name_test"
        )
