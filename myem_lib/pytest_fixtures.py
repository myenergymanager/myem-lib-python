"""Builtins Fixtures."""
import os
from random import randint
from unittest.mock import Mock
import jwt
import pytest
from sqlalchemy import create_engine
from myem_lib.utils import get_private_key, get_public_key
from uuid import uuid4


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
    from nameko.cli import setup_config
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
def db_dependency_factory(request):
    """Create a database dependency for sqlalchemy tests."""
    # Do not import testing at the top, otherwise it will create problems with request lib
    # https://github.com/nameko/nameko/issues/693
    # https://github.com/gevent/gevent/issues/1016#issuecomment-328529454
    sqlalchemy_testing_url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )

    engine = create_engine(sqlalchemy_testing_url)

    def make_db_dependency(DeclarativeBase):
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
    from nameko.testing.utils import get_extension
    from nameko.containers import ServiceContainer


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
    yield {
        "token": jwt.encode({"id": randint(1, 100000)}, get_private_key(), algorithm="RS256"),
        "public_key": get_public_key(),
        "private_key": get_private_key(),
    }


@pytest.fixture(scope="session")
def user_token_2():
    """Generate token fixture."""
    yield {
        "token": jwt.encode({"id": randint(1, 100000)}, get_private_key(1), algorithm="RS256"),
        "public_key": get_public_key(1),
        "private_key": get_private_key(1),
    }


@pytest.fixture(scope="session")
def installer_token():
    """Generate token fixture."""
    yield {
        "token": jwt.encode({"id": str(uuid4())}, get_private_key(), algorithm="RS256"),
        "public_key": get_public_key(),
        "private_key": get_private_key(),
    }


@pytest.fixture(scope="session")
def installer_token_2():
    """Generate token fixture."""
    yield {
        "token": jwt.encode({"id": str(uuid4())}, get_private_key(1), algorithm="RS256"),
        "public_key": get_public_key(1),
        "private_key": get_private_key(1),
    }
