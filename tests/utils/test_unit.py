import json
import os
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from myem_lib.db_settings_mixins import DbSettingsMixin
from myem_lib.jwt_settings_mixins import JwtSettingsMixin
from myem_lib.test_data.equipments import equipments
from myem_lib.test_data.installation_requests import installation_requests
from myem_lib.test_data.installer_clients import clients, comments
from myem_lib.test_data.ui_notifications import notifications
from myem_lib.test_data.user_management import roles, users
from myem_lib.test_data.windev_legacy import (
    addresses,
    consents,
    consents_sources,
    customers,
    formulas,
    meter_metrics,
    meters,
)
from myem_lib.test_data.windev_legacy import users as simple_users
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


class TestData:
    def test_installer_clients_data(self):
        for client in clients:
            assert all(key in ["id", "user_id", "installer_id"] for key, item in client.items())
        for comment in comments:
            assert all(key in ["id", "client_id", "message"] for key, item in comment.items())

    def test_user_management_data(self):
        for user in users:
            assert all(
                key
                in [
                    "id",
                    "email",
                    "hashed_password",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "first_name",
                    "last_name",
                    "phone",
                    "address",
                    "role",
                ]
                for key, item in user.items()
            )
        for role in roles:
            assert all(key in ["id", "name", "description"] for key, item in role.items())

    def test_ui_notifications_data(self):
        for notification in notifications:
            assert all(
                key in ["id", "user_id", "title", "content", "status", "redirect_to"]
                for key, item in notification.items()
            )

    def test_installation_requests_data(self):
        for installation_request in installation_requests:
            assert all(
                key
                in [
                    "id",
                    "user_id",
                    "status",
                    "budget",
                    "equipment_type",
                    "equipment_brand",
                    "equipment_model",
                    "comment",
                ]
                for key, item in installation_request.items()
            )

    def test_equipments_data(self):
        for equipment in equipments:
            assert all(
                key in ["id", "user_id", "type", "brand", "reference", "installed_at"]
                for key, item in equipment.items()
            )

    def test_windev_legacy_data(self):
        for consent in consents:
            assert all(
                key in ["id", "id_meter", "id_consent_source", "revoked_at", "meta_data"]
                for key, item in consent.items()
            )
        for consent_source in consents_sources:
            assert all(key in ["id", "name"] for key, item in consent_source.items())
        for meter in meters:
            assert all(
                key in ["id", "guid", "name", "customer_id", "created_at", "updated_at"]
                for key, item in meter.items()
            )
        for customer in customers:
            assert all(
                key in ["id", "id_formula", "created_at", "updated_at", "id_address"]
                for key, item in customer.items()
            )
        for simple_user in simple_users:
            assert all(
                key
                in [
                    "id",
                    "email",
                    "firstname",
                    "lastname",
                    "phone",
                    "type",
                    "created_at",
                    "customer_id",
                ]
                for key, item in simple_user.items()
            )
        for meter_metric in meter_metrics:
            assert all(
                key in ["id", "meter_id", "created_at"] for key, item in meter_metric.items()
            )

        for address in addresses:
            assert all(
                key
                in [
                    "id_address",
                    "street",
                    "postal_code",
                    "additional_data",
                    "city",
                    "country",
                    "latitude",
                    "longitude",
                ]
                for key, item in address.items()
            )

        for formula in formulas:
            assert all(key in ["id", "title"] for key, item in formula.items())
