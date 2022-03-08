"""Throttle Mixins Nameko."""
import logging
import time
from datetime import datetime
from typing import Any, Dict

from kombu import Connection, Exchange, Producer
from nameko import config
from nameko.rpc import rpc


class ThrottleMixinsNameko:
    """ThrottleMixinsNameko."""

    __thtmxn_timer = datetime.now().replace(second=0, microsecond=0)
    __thtmxn_hits = 0
    __thtmxn_max_hits = 10
    thtmxn_routing_key = "requester"
    thtmxn_exchange_name = "requester"
    thtmxn_queue_name = "queue"

    @rpc
    def call_with_throttle(self, function_name: str, **kwargs: Any) -> None:
        """Call with throttle."""
        kwargs["function_name"] = function_name
        with Connection(config["AMQP_URI"]) as conn:
            with conn.channel() as channel:
                exchange = Exchange(self.thtmxn_exchange_name)
                producer = Producer(channel)
                producer.publish(
                    body=kwargs,
                    exchange=exchange,
                    declare=[exchange],
                    routing_key=self.thtmxn_routing_key,
                    serializer="pickle",
                )

    # todo today, we have to implement this in the child because of Queue params, if we use this
    # todo params in the parent it will not take the child params in consideration so for the
    # todo moment we reimplement it, we have to find a solution maybe with using metaclass and NEW
    # @consume(
    #     Queue(
    #         thtmxn_queue_name,
    #         exchange=Exchange(thtmxn_exchange_name),
    #         routing_key=thtmxn_routing_key,
    #     )
    # )
    # def consume_messages(self, body: Dict[str, Any]) -> None:
    #     """Consume incoming requests to requester queue."""
    #     self.consume_requests_with_time_condition(body=body)

    def consume_requests_with_time_condition(self, body: Dict[str, Any]) -> None:
        """Consume "thtmxn_hits" requests in one minute."""
        if ThrottleMixinsNameko.__thtmxn_timer == datetime.now().replace(second=0, microsecond=0):
            if ThrottleMixinsNameko.__thtmxn_hits == ThrottleMixinsNameko.__thtmxn_max_hits:
                time.sleep(60 - datetime.now().second)
                ThrottleMixinsNameko.__thtmxn_hits = 0
                ThrottleMixinsNameko.__thtmxn_timer = datetime.now().replace(
                    second=0, microsecond=0
                )
        else:
            ThrottleMixinsNameko.__thtmxn_hits = 0
            ThrottleMixinsNameko.__thtmxn_timer = datetime.now().replace(second=0, microsecond=0)
        ThrottleMixinsNameko.__thtmxn_hits += 1
        logging.error(f"ThrottleMixinsNameko : {ThrottleMixinsNameko.__thtmxn_hits}")

        self.throttle_call(**body)

    def throttle_call(self, **kwargs: Any) -> None:
        """Call functions depending on function_name parameter."""
        pass
