import os
import pytest
from nameko.containers import ServiceContainer
from nameko_sqlalchemy import DatabaseSession, DB_URIS_KEY
from unittest.mock import Mock
from nameko.cli import setup_config


@pytest.fixture(scope="session", autouse=True)
def override_amqp_api_uri_from_env(request):
    # ovewrite rabbitmq_uri from test config of nameko
    request.config.option.RABBIT_API_URI = (
        f'http://guest:guest@{os.environ.get("RABBITMQ_HOST")}:15672'
    )
    request.config.option.RABBIT_AMQP_URI = (
        f'pyamqp://guest:guest@{os.environ.get("RABBITMQ_HOST")}:5672/'
    )


@pytest.fixture(scope="session")
def load_yml():
    with open("config.yml", "rb") as file_stream:
        setup_config(file_stream)


@pytest.fixture(scope="function")
# you need to keep rabbit config to make sure this function is called after rabbit_config
def integration_config(load_yml, rabbit_config):
    yield


@pytest.fixture(scope="module")
def db_dependency(load_yml, request):
    # Do not import testing at the top, otherwise it will create problems with request lib
    # https://github.com/nameko/nameko/issues/693
    # https://github.com/gevent/gevent/issues/1016#issuecomment-328529454
    from nameko.testing.utils import get_extension
    declarative_base = request.param

    class Service:
        name = "db_load_service"

        db = DatabaseSession(declarative_base)
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
    declarative_base.metadata.drop_all(provider.engine)
    declarative_base.metadata.create_all(provider.engine)
    yield provider.get_dependency(Mock())
    declarative_base.metadata.drop_all(provider.engine)
    provider.stop()
