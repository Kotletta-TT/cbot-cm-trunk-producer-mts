from typing import Callable, Optional
from threading import Thread
import logging

from pika import (
    BlockingConnection,
    ConnectionParameters,
)
from pika.credentials import (
    PlainCredentials,
)
from pika.adapters.blocking_connection import (
    BlockingChannel
)
from pika.spec import BasicProperties

from conf import (
    RABBIT_HOST,
    RABBIT_PASS,
    RABBIT_PORT,
    RABBIT_USERNAME,
    RABBIT_VHOST)


logging.getLogger("pika").setLevel(logging.WARNING)


class RMQConsumer:
    __cr: PlainCredentials
    __cp: ConnectionParameters
    __thread: Thread

    def __init__(self) -> None:
        self.__cr = PlainCredentials(
            username=RABBIT_USERNAME,
            password=RABBIT_PASS
        )
        self.__cp = ConnectionParameters(
            host=RABBIT_HOST,
            port=RABBIT_PORT,
            virtual_host=RABBIT_VHOST,
            credentials=self.__cr
        )

    def consume(
        self,
        exchange: str,
        queue: str,
        func: Callable,
        use_dead_ex: Optional[bool] = True,
        durable: bool = True,
        exchange_type: str = 'fanout',
    ) -> None:
        connection = BlockingConnection(
            parameters=self.__cp
        )
        channel = connection.channel()

        if use_dead_ex:
            channel.exchange_declare(
                exchange=f"{exchange}-dead",
                exchange_type=exchange_type,
                durable=durable,
            )
            channel.queue_declare(
                queue=f"{queue}-dead",
                durable=durable,
            )
            channel.queue_bind(
                queue=f"{queue}-dead",
                exchange=f"{exchange}-dead",
                routing_key='',
            )

        channel.exchange_declare(
            exchange=exchange,
            exchange_type=exchange_type,
            durable=True,
        )
        arguments = {
            "x-dead-letter-exchange": f"{exchange}-dead",
        } if use_dead_ex else {}
        channel.queue_declare(
            queue=queue,
            durable=durable,
            arguments=arguments,
        )
        channel.queue_bind(
            queue=queue,
            exchange=exchange,
            routing_key='',
        )
        channel.basic_consume(
            queue=queue,
            on_message_callback=func,
        )

        self.__thread = Thread(
            target=self._thread_run,
            args=(connection, channel),
        )
        self.__thread.start()

    def _thread_run(
        self,
        connection: BlockingConnection,
        channel: BlockingChannel,
    ) -> None:
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        connection.close()

    def publish(
        self,
        exchange: str,
        message: str,
        exchange_type: str = 'fanout',
        persistent: bool = False,
        durable: bool = True,
    ) -> None:
        connection = BlockingConnection(
            parameters=self.__cp
        )
        channel = connection.channel()

        channel.exchange_declare(
            exchange=exchange,
            exchange_type=exchange_type,
            durable=durable,
        )

        channel.basic_publish(
            exchange=exchange,
            routing_key='',
            body=message,
            properties=BasicProperties(
                delivery_mode=2 if persistent else 1
            )
        )

        connection.close()
