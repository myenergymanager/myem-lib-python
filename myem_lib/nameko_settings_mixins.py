"""Nameko Settings Mixins."""
import os
from typing import Any

from nameko import config
from nameko.standalone.rpc import ClusterRpcClient


class NamekoSettingsMixin:
    """Nameko settings mixin."""

    network_rabbitmq_uri = os.environ["RABBITMQ_URI"] if os.getenv("RABBITMQ_URI") else os.environ["RPC_RABBITMQ_URI"]

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
