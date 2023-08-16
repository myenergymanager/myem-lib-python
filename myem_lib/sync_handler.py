"""Sync handler."""
import logging
from typing import Any, Literal, TypedDict

from kombu import Connection, Exchange, Producer
from nameko_sqlalchemy import DatabaseSession


class RowToSyncType(TypedDict):
    """Row To Sync Type."""

    identifiers: list[list[Any]]
    op: Literal["DELETE", "UPDATE"]
    columns_to_sync: dict[str, Any] | None


class DbSyncConsumer:
    """Db Consumer.

    Usage
    you have to inherit this class in the service you want to use.
    Example
    class NrlinkMetricsService(DbSyncConsumer):
        name = "backbone_metrics_nrlink_service"
        db = DatabaseSession(DeclarativeBase, engine_options={"pool_pre_ping": True})
        models = [NrlinkConsumptionMetric, NrLinkInternalTemperatureMetric, NrLinkPowerMetric]
        @consume(
        Queue(
            f"{name}_queue",
            exchange=Exchange(f"{name}_exchange"),
            routing_key=f"{name}_routing_key",
            ),
        )
        def consume_messages(self, body: dict[str, Any]) -> None:
            self.sync_db_model(body)
    """

    models: Any = []
    db: DatabaseSession
    name: str

    def get_model(self, table_name: str) -> Any | None:
        """Get model from table name if existed."""
        for model in self.models:
            if model.__tablename__ == table_name:
                return model
        return None

    @staticmethod
    def format_sql_filter(model: Any, identifiers: list[list[Any]]) -> list[Any]:
        """Format sql filter."""
        _filter = []
        for filer_row in identifiers:
            column, op, value = filer_row
            if op == "==":
                _filter.append(getattr(model, column) == value)
            elif op == "!=":
                _filter.append(getattr(model, column) != value)
            elif op == "in_":
                _filter.append(getattr(model, column).in_(value))
            elif op == "notin_":
                _filter.append(getattr(model, column).notin_(value))
            elif op == "is_":
                _filter.append(getattr(model, column).is_(value))
            elif op == "not_":
                _filter.append(getattr(model, column).not_(value))
            elif op == ">=":
                _filter.append(getattr(model, column) >= value)
            elif op == ">":
                _filter.append(getattr(model, column) > value)
            elif op == "<":
                _filter.append(getattr(model, column) < value)
            elif op == "<=":
                _filter.append(getattr(model, column) <= value)
            else:
                raise Exception("Unkown operator consider handle this one !")
        return _filter

    def sync_db_model(self, body: dict[str, Any]) -> None:
        """Sync db models."""
        logging.info("db sync request has arrived !")
        for table_name, rows_to_sync in body.items():
            if not (model := (self.get_model(table_name))):
                raise Exception(f"table {table_name} doesn't exist !")
            logging.info(f"syncing table {table_name}")
            for row_to_sync in rows_to_sync:
                _filter = self.format_sql_filter(model, row_to_sync["identifiers"])
                query = self.db.query(model).filter(*_filter)
                if row_to_sync["op"] == "DELETE":
                    query.delete()
                    self.db.commit()
                elif row_to_sync["op"] == "UPDATE":
                    query.update(row_to_sync["columns_to_sync"])
                    self.db.commit()
                else:
                    raise Exception(f"Invalid operation {row_to_sync['op']} !")

    # this commented code needs to be putted in the child class
    # @consume(
    #     Queue(
    #         f"{name}_queue",
    #         exchange=Exchange(f"{name}_exchange"),
    #         routing_key=f"{name}_routing_key",
    #     ),
    # )
    # def consume_messages(self, body: dict[str, Any]) -> None:
    #     """Consume incoming requests to requester queue."""
    #
    #     self.sync_db_model(body)


class DbSyncPublisher:
    """Db sync Publisher.

    After deleting some data if other data in another microservice needs to be synchronized.
    (UPDATE OR DELETE) we use this class to send a request in the queue by providing the required
    information's.
    """

    @staticmethod
    def sync_model(
        rabbitmq_uri: str,
        service_name: str,
        data: dict[str, list[RowToSyncType]],
    ) -> None:
        """Call the db sync service.

            usage example:
                DbSyncPublisher.sync_model(
            rabbitmq_uri=os.environ["RABBITMQ_URI"],
            service_name="backbone_metrics_nrlink_service",
            data={
                "nrlink_consumption_metrics": [{
                    "identifiers": [["meter_guid", "==", consent.meter_guid]],
                    "op": "DELETE",
                }],
                "nrlink_internal_temperature_metrics": [{
                    "identifiers": [["meter_guid", "==", consent.meter_guid]],
                    "op": "DELETE",
                }],
                "nrlink_power_metrics": [{
                    "identifiers": [["meter_guid", "==", consent.meter_guid]],
                    "op": "UPDATE",
                    "columns_to_sync": {"created_at": datetime.now()}
                }],
            },
        )
        """
        logging.info(f"sending sync request to rabbitmq {rabbitmq_uri}, service {service_name}")
        with Connection(rabbitmq_uri) as conn:
            with conn.channel() as channel:
                exchange = Exchange(f"{service_name}_exchange")
                producer = Producer(channel)
                producer.publish(
                    body=data,
                    exchange=exchange,
                    declare=[exchange],
                    routing_key=f"{service_name}_routing_key",
                    serializer="pickle",
                )
