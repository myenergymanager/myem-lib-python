"""Nameko Settings Mixins."""
from __future__ import absolute_import

import os
import uuid
from typing import Any

from kombu.messaging import Queue

from nameko import config, serialization
from nameko.constants import (
    AMQP_SSL_CONFIG_KEY, AMQP_URI_CONFIG_KEY, CALL_ID_STACK_CONTEXT_KEY,
    DEFAULT_AMQP_URI, LOGIN_METHOD_CONFIG_KEY
)
from nameko.containers import new_call_id
from nameko.extensions import DependencyProvider
from nameko.messaging import encode_to_headers
from nameko.rpc import (
    RESTRICTED_PUBLISHER_OPTIONS, RPC_REPLY_QUEUE_TEMPLATE, Client, get_rpc_exchange
)
from nameko.standalone.rpc import ClusterRpcClient, ReplyListener


class NamekoSettingsMixin:
    """Nameko settings mixin."""

    network_rabbitmq_uri = os.environ["RABBITMQ_URI"]

    backbone_rabbitmq_uri = os.getenv("BACKBONE_RABBITMQ_URI")

    network_cluster_rpc_proxy_config = {
        "serializer": "pickle",
        "AMQP_URI": network_rabbitmq_uri,
    }
    backbone_cluster_rpc_proxy_config = {
        "serializer": "pickle",
        "AMQP_URI": backbone_rabbitmq_uri,
    }


class NetworkClusterRpcClient(ClusterRpcClient):
    """Network Cluster Rpc Client.

    This cluster is used to make call to services in the same network.
    Using the environment variable RABBITMQ_URI, serializer is pickle by default.
    with NetworkClusterRpcClient() as network_rpc:
        guids = network_rpc.customer_center_service.get_user_meters_guid(
            user_id=user_id
        )
    """

    def __init__(
        self, context_data: Any = None, timeout: int | None = 70, **publisher_options: Any
    ) -> None:
        """An override of Cluster Rpc Client to add config setup."""
        # serializer in the publisher_options dict is not used when initializing ReplyListener
        # in order to pass this bug we set by default config["serializer"] to pickle if it's not
        # already set up
        publisher_options["uri"] = os.environ["RABBITMQ_URI"]
        publisher_options["serializer"] = "pickle"
        config["serializer"] = config.get("serializer", publisher_options["serializer"])
        super().__init__(context_data=context_data, timeout=timeout, **publisher_options)


class BackboneClusterRpcClient(ClusterRpcClient):
    """Backbone Cluster Rpc Client.

    This cluster is used to make call to services in backbone network.
    Using the environment variable BACKBONE_RABBITMQ_URI, serializer is pickle by default
    with BackboneClusterRpcClient() as backbone_rpc:
        res = backbone_rpc.commercial_offers.get_contract_periods()
    """

    def __init__(
        self, context_data: Any = None, timeout: int | None = 70, **publisher_options: Any
    ) -> None:
        """An override of Cluster Rpc Client to add config setup."""
        publisher_options["uri"] = os.environ["BACKBONE_RABBITMQ_URI"]
        publisher_options["serializer"] = "pickle"
        config["serializer"] = config.get("serializer", publisher_options["serializer"])
        super().__init__(context_data=context_data, timeout=timeout, **publisher_options)


class CustomClusterRpcClient(ClusterRpcClient):
    """Custom Cluster Rpc Client.

    This cluster is used to make call to services in the same network.
    Using variable env rabbitmq_uri, serializer is pickle by default.
    with CustomClusterRpcClient(rabbitmq_uri="put_your_rabbitmq_uri_here") as data_rabbitmq_rpc:
        guids = data_rabbitmq_rpc.bl_metrics.get_data(
            user_id=user_id
        )
    """

    def __init__(
        self,
        rabbitmq_uri: str,
        context_data: Any = None,
        timeout: int | None = 70,
        **publisher_options: Any
    ) -> None:
        """An override of Cluster Rpc Client to add config setup."""
        publisher_options["uri"] = rabbitmq_uri
        publisher_options["serializer"] = "pickle"
        config["serializer"] = config.get("serializer", publisher_options["serializer"])
        super().__init__(context_data=context_data, timeout=timeout, **publisher_options)


class ClusterRpcClientDurableQueue(ClusterRpcClient):
    def __init__(
        self, context_data=None, timeout=None, **publisher_options
    ):
        self.uuid = str(uuid.uuid4())

        exchange = get_rpc_exchange()

        queue_name = RPC_REPLY_QUEUE_TEMPLATE.format(
            "standalone_rpc_client", self.uuid
        )
        queue = Queue(
            queue_name,
            exchange=exchange,
            routing_key=self.uuid,
            queue_arguments={}  # no expiration time when stops the service delete the queue
        )

        self.amqp_uri = publisher_options.pop(
            'uri', config.get(AMQP_URI_CONFIG_KEY, DEFAULT_AMQP_URI)
        )
        self.ssl = publisher_options.pop(
            'ssl', config.get(AMQP_SSL_CONFIG_KEY)
        )
        self.login_method = publisher_options.pop(
            'login_method', config.get(LOGIN_METHOD_CONFIG_KEY)
        )

        self.reply_listener = ReplyListener(
            queue, timeout=timeout, uri=self.amqp_uri, ssl=self.ssl
        )

        serialization_config = serialization.setup()
        self.serializer = publisher_options.pop(
            'serializer', serialization_config.serializer
        )

        for option in RESTRICTED_PUBLISHER_OPTIONS:
            publisher_options.pop(option, None)

        publisher = self.publisher_cls(
            self.amqp_uri,
            ssl=self.ssl,
            login_method=self.login_method,
            exchange=exchange,
            serializer=self.serializer,
            declare=[self.reply_listener.queue],
            reply_to=self.reply_listener.queue.routing_key,
            **publisher_options
        )

        context_data = context_data or {}

        def publish(*args, **kwargs):

            context_data[CALL_ID_STACK_CONTEXT_KEY] = [
                'standalone_rpc_client.{}.{}'.format(self.uuid, new_call_id())
            ]

            extra_headers = kwargs.pop('extra_headers')
            extra_headers.update(encode_to_headers(context_data))

            publisher.publish(
                *args, extra_headers=extra_headers, **kwargs
            )

        get_reply = self.reply_listener.register_for_reply

        self.client = Client(publish, get_reply, context_data)


class ClusterRpcProxy(DependencyProvider):
    def __init__(
        self, rabbitmq_uri, serializer
    ):
        self.rabbitmq_uri = rabbitmq_uri
        self.serializer = serializer

    def setup(self):
        self.cluster_rpc_proxy = ClusterRpcClientDurableQueue(uri=self.rabbitmq_uri, serializer=self.serializer)
        self.cluster_rpc_proxy.reply_listener.start()

    def stop(self):
        self.cluster_rpc_proxy.reply_listener.stop()
        self.cluster_rpc_proxy.stop()

    def kill(self):
        self.cluster_rpc_proxy.reply_listener.stop()
        self.cluster_rpc_proxy.stop()

    def get_dependency(self, worker_ctx):
        return self.cluster_rpc_proxy.client

    def worker_teardown(self, worker_ctx):
        pass
