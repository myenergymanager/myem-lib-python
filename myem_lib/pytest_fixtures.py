"""Builtins Fixtures."""
import os
from random import randint
from unittest.mock import Mock

import jwt
import pytest
from Crypto.PublicKey import RSA
from nameko.cli import setup_config
from nameko.containers import ServiceContainer


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
    with open("config.yml", "rb") as file_stream:
        setup_config(file_stream)


@pytest.fixture(scope="function")
# we override rabbit config to use config yml
def rabbit_config(load_yml, rabbit_config):
    """Override rabbit config fixture to call load_yml fixture."""
    yield


# for this fixture, we tried different solutions
# we already tried with parametrize https://docs.pytest.org/en/6.2.x/
# fixture.html#fixture-parametrize
# the problem is that this solution cannot be wrapped in another
# fixture (cannot use parametrize for a fixture)
# So, we decided to use factories as fixture
# https://docs.pytest.org/en/latest/how-to/fixtures.html#factories-as-fixtures
@pytest.fixture(scope="module")
def db_dependency_factory(load_yml, request):
    """Create a database dependency for sqlalchemy tests."""
    # Do not import testing at the top, otherwise it will create problems with request lib
    # https://github.com/nameko/nameko/issues/693
    # https://github.com/gevent/gevent/issues/1016#issuecomment-328529454
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


@pytest.fixture
def generate_keys():
    """Generate asymmetric RSA keys."""
    key = RSA.generate(2048)
    print(key.publickey().exportKey)
    return {"private_key": key.exportKey(), "public_key": key.publickey().exportKey()}


@pytest.fixture
def generate_token(monkeypatch, generate_keys):
    """Generate a token."""
    return "KEY " + jwt.encode(
        {"id": randint(1, 100000)}, generate_keys["private_key"], algorithm="RS256"
    )


@pytest.fixture
def generate_another_token(monkeypatch, generate_keys):
    """Generate another token."""
    return "KEY " + jwt.encode(
        {"id": randint(1, 100000)}, generate_keys["private_key"], algorithm="RS256"
    )
