"""Builtins Fixtures."""
import os
from random import randint
from unittest.mock import Mock, MagicMock
from uuid import uuid4

import jwt
import pytest


@pytest.fixture(scope="session", autouse=True)
def override_amqp_api_uri_from_env(request):
    """Overwrite rabbitmq_uri from test config of nameko."""
    request.config.option.RABBIT_API_URI = (
        f'http://guest:guest@{os.environ.get("RABBITMQ_HOST")}:15672'
    )
    request.config.option.RABBIT_AMQP_URI = (
        f'pyamqp://guest:guest@{os.environ.get("RABBITMQ_HOST")}:5672/'
    )


@pytest.fixture(scope="session")
def load_yml():
    """Load config.yml file."""
    from nameko.cli import setup_config

    with open("config.yml", "rb") as file_stream:
        setup_config(file_stream)


@pytest.fixture(scope="function")
# we override rabbit config to use config yml
def rabbit_config(load_yml, rabbit_config):
    """Override rabbit config fixture to call load_yml fixture."""
    yield


@pytest.fixture()
def rabbit_config_integration(load_yml, request, rabbit_manager):
    """Override rabbit config fixture for integration tests."""

    # this fixture will not create a vhost

    from six.moves.urllib.parse import urlparse  # pylint: disable=E0401

    rabbit_amqp_uri = request.config.getoption("RABBIT_AMQP_URI")
    uri_parts = urlparse(rabbit_amqp_uri)
    username = uri_parts.username

    amqp_uri = "{uri.scheme}://{uri.netloc}/".format(uri=uri_parts)

    conf = {"AMQP_URI": amqp_uri, "username": username}

    yield conf


# for this fixture, we tried different solutions
# we already tried with parametrize https://docs.pytest.org/en/6.2.x/
# fixture.html#fixture-parametrize
# the problem is that this solution cannot be wrapped in another
# fixture (cannot use parametrize for a fixture)
# So, we decided to use factories as fixture
# https://docs.pytest.org/en/latest/how-to/fixtures.html#factories-as-fixtures
@pytest.fixture(scope="module")
def db_dependency_factory(request):
    """Create a database dependency for sqlalchemy tests."""

    from sqlalchemy import create_engine

    # Do not import testing at the top, otherwise it will create problems with request lib
    # https://github.com/nameko/nameko/issues/693
    # https://github.com/gevent/gevent/issues/1016#issuecomment-328529454
    sqlalchemy_testing_url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )

    engine = create_engine(sqlalchemy_testing_url)

    def make_db_dependency(DeclarativeBase):
        DeclarativeBase.metadata.drop_all(bind=engine)
        DeclarativeBase.metadata.create_all(bind=engine)
        # service = ServiceContainer(Service)
        # provider = get_extension(service, DatabaseSession)
        # # simulate db uris with the first existing one from yml file.
        # provider.setup()

        def clean():
            DeclarativeBase.metadata.drop_all(bind=engine)

        request.addfinalizer(clean)
        return engine

    yield make_db_dependency


@pytest.fixture(scope="module")
def nameko_db_dependency_factory(load_yml, request):
    """Create a database dependency for sqlalchemy tests."""
    # Do not import testing at the top, otherwise it will create problems with request lib
    # https://github.com/nameko/nameko/issues/693
    # https://github.com/gevent/gevent/issues/1016#issuecomment-328529454
    from nameko.containers import ServiceContainer
    from nameko.testing.utils import get_extension

    # move it here to avoid error if no database
    from nameko_sqlalchemy import DatabaseSession, DB_URIS_KEY

    def make_db_dependency(DeclarativeBase):
        class Service:
            name = "db_load_service"

            db = DatabaseSession(DeclarativeBase)
            from nameko.testing.services import dummy

            @dummy
            def dummy(self):
                pass

        service = ServiceContainer(Service)
        provider = get_extension(service, DatabaseSession)
        # simulate db uris with the first existing one from yml file.
        provider.container.config[DB_URIS_KEY]["db_load_service:Base"] = list(
            provider.container.config[DB_URIS_KEY].values()
        )[0]
        provider.setup()
        DeclarativeBase.metadata.drop_all(provider.engine)
        DeclarativeBase.metadata.create_all(provider.engine)

        def clean():
            DeclarativeBase.metadata.drop_all(provider.engine)
            provider.stop()

        request.addfinalizer(clean)
        return provider.get_dependency(Mock())

    yield make_db_dependency


@pytest.fixture(scope="session")
def user_token():
    """Generate token fixture."""
    from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
    yield {
        "token": jwt.encode({"id": randint(1, 100000)}, FastApiSettingsMixin.get_private_key(), algorithm="RS256"),
        "public_key": FastApiSettingsMixin.get_public_key(),
        "private_key": FastApiSettingsMixin.get_private_key(),
    }


@pytest.fixture(scope="session")
def user_token_2():
    """Generate token fixture."""
    from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
    yield {
        "token": jwt.encode({"id": randint(1, 100000)}, FastApiSettingsMixin.get_private_key(1), algorithm="RS256"),
        "public_key": FastApiSettingsMixin.get_public_key(1),
        "private_key": FastApiSettingsMixin.get_private_key(1),
    }


@pytest.fixture(scope="session")
def ng_user_token():
    """Generate token fixture."""
    from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
    yield {
        "token": jwt.encode(
            {"id": str(uuid4()), "role": "installer"}, FastApiSettingsMixin.get_private_key(), algorithm="RS256"
        ),
        "public_key": FastApiSettingsMixin.get_public_key(),
        "private_key": FastApiSettingsMixin.get_private_key(),
    }


@pytest.fixture(scope="session")
def ng_user_token_2():
    """Generate token fixture."""
    from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
    yield {
        "token": jwt.encode(
            {"id": str(uuid4()), "role": "installer"}, FastApiSettingsMixin.get_private_key(1), algorithm="RS256"
        ),
        "public_key": FastApiSettingsMixin.get_public_key(1),
        "private_key": FastApiSettingsMixin.get_private_key(1),
    }


@pytest.fixture(scope="session")
def ng_distributor_token():
    """Generate token fixture."""
    from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
    yield {
        "token": jwt.encode(
            {"id": str(uuid4()), "role": "distributor"}, FastApiSettingsMixin.get_private_key(), algorithm="RS256"
        ),
        "public_key": FastApiSettingsMixin.get_public_key(),
        "private_key": FastApiSettingsMixin.get_private_key(),
    }


@pytest.fixture(scope="session")
def ng_distributor_token_2():
    """Generate token fixture."""
    from myem_lib.fast_api_settings_mixins import FastApiSettingsMixin
    yield {
        "token": jwt.encode(
            {"id": str(uuid4()), "role": "distributor"}, FastApiSettingsMixin.get_private_key(1), algorithm="RS256"
        ),
        "public_key": FastApiSettingsMixin.get_public_key(1),
        "private_key": FastApiSettingsMixin.get_private_key(1),
    }


def dummy_func(*args, **kwargs):
    return None


@pytest.fixture
def mock_network_nameko_cluster(monkeypatch):
    from myem_lib.nameko_settings_mixins import NetworkClusterRpcClient
    def set_mock(*args):
        cluster = MagicMock()

        for dict_mock in args:
            if isinstance(dict_mock["mocked_response"], Exception):
                setattr(
                    getattr(
                        getattr(cluster, dict_mock["service_name"]),
                        dict_mock["function_name"],
                    ),
                    "side_effect",
                    dict_mock["mocked_response"],
                )
            else:
                setattr(
                    getattr(
                        getattr(cluster, dict_mock["service_name"]),
                        dict_mock["function_name"],
                    ),
                    "return_value",
                    dict_mock["mocked_response"],
                )
                setattr(
                    getattr(
                        getattr(
                            getattr(cluster, dict_mock["service_name"]),
                            dict_mock["function_name"],
                        ),
                        "call_async",
                    ),
                    "return_value",
                    None,
                )

        def __enter__(*args, **kwargs):
            return cluster

        monkeypatch.setattr(NetworkClusterRpcClient, "__init__", dummy_func)
        monkeypatch.setattr(NetworkClusterRpcClient, "__enter__", __enter__)
        monkeypatch.setattr(NetworkClusterRpcClient, "__exit__", dummy_func)

        return cluster

    yield set_mock


@pytest.fixture
def mock_backbone_nameko_cluster(monkeypatch):
    from myem_lib.nameko_settings_mixins import BackboneClusterRpcClient
    def set_mock(*args):
        cluster = MagicMock()

        for dict_mock in args:
            if isinstance(dict_mock["mocked_response"], Exception):
                setattr(
                    getattr(
                        getattr(cluster, dict_mock["service_name"]),
                        dict_mock["function_name"],
                    ),
                    "side_effect",
                    dict_mock["mocked_response"],
                )
            else:
                setattr(
                    getattr(
                        getattr(cluster, dict_mock["service_name"]),
                        dict_mock["function_name"],
                    ),
                    "return_value",
                    dict_mock["mocked_response"],
                )
                setattr(
                    getattr(
                        getattr(
                            getattr(cluster, dict_mock["service_name"]),
                            dict_mock["function_name"],
                        ),
                        "call_async",
                    ),
                    "return_value",
                    None,
                )

        def __enter__(*args, **kwargs):
            return cluster

        monkeypatch.setattr(BackboneClusterRpcClient, "__init__", dummy_func)
        monkeypatch.setattr(BackboneClusterRpcClient, "__enter__", __enter__)
        monkeypatch.setattr(BackboneClusterRpcClient, "__exit__", dummy_func)

        return cluster

    yield set_mock


@pytest.fixture
def mock_custom_nameko_cluster(monkeypatch):
    from myem_lib.nameko_settings_mixins import CustomClusterRpcClient

    def set_mock(*args):
        cluster = MagicMock()

        for dict_mock in args:
            if isinstance(dict_mock["mocked_response"], Exception):
                setattr(
                    getattr(
                        getattr(cluster, dict_mock["service_name"]),
                        dict_mock["function_name"],
                    ),
                    "side_effect",
                    dict_mock["mocked_response"],
                )
            else:
                setattr(
                    getattr(
                        getattr(cluster, dict_mock["service_name"]),
                        dict_mock["function_name"],
                    ),
                    "return_value",
                    dict_mock["mocked_response"],
                )
                setattr(
                    getattr(
                        getattr(
                            getattr(cluster, dict_mock["service_name"]),
                            dict_mock["function_name"],
                        ),
                        "call_async",
                    ),
                    "return_value",
                    None,
                )

        def __enter__(*args, **kwargs):
            return cluster

        monkeypatch.setattr(CustomClusterRpcClient, "__init__", dummy_func)
        monkeypatch.setattr(CustomClusterRpcClient, "__enter__", __enter__)
        monkeypatch.setattr(CustomClusterRpcClient, "__exit__", dummy_func)

        return cluster

    yield set_mock
