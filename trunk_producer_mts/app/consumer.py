from threading import Thread
from typing import Callable, Optional

from pika import (
    BlockingConnection,
    ConnectionParameters,
)
from pika.adapters.blocking_connection import (
    BlockingChannel
)
from pika.credentials import (
    PlainCredentials,
)

from conf import (
    RABBIT_HOST,
    RABBIT_PASS,
    RABBIT_PORT,
    RABBIT_USERNAME,
    RABBIT_VHOST)


class RMQConsumer:
    __connection: BlockingConnection
    __channel: BlockingChannel
    __thread: Thread

    def __init__(self) -> None:
        self.__connect()

    def __connect(self) -> None:
        # pylint: disable=too-many-boolean-expressions
        if (
                not hasattr(self, '__connection')
                or not self.__connection.is_open
                or not self.__connection.is_closed
                or not hasattr(self, '__channel')
                or not self.__channel.is_open
                or self.__channel.is_closed
        ):
            cr = PlainCredentials(
                username=RABBIT_USERNAME,
                password=RABBIT_PASS
            )
            cp = ConnectionParameters(
                host=RABBIT_HOST,
                port=RABBIT_PORT,
                virtual_host=RABBIT_VHOST,
                credentials=cr
            )
            self.__connection = BlockingConnection(
                parameters=cp
            )
            self.__channel = self.__connection.channel()

    def consume(
            self,
            exchange: str,
            queue: str,
            func: Callable,
            use_dead_ex: Optional[bool] = True,
            durable: bool = True,
            exchange_type: str = 'fanout',
    ) -> None:
        if use_dead_ex:
            self.__channel.exchange_declare(
                exchange=f"{exchange}-dead",
                exchange_type=exchange_type,
                durable=True,
            )
            self.__channel.queue_declare(
                queue=f"{queue}-dead",
                durable=durable,
            )
            self.__channel.queue_bind(
                queue=f"{queue}-dead",
                exchange=f"{exchange}-dead",
                routing_key='',
            )

        self.__channel.exchange_declare(
            exchange=exchange,
            exchange_type=exchange_type,
            durable=True,
        )
        arguments = {
            "x-dead-letter-exchange": f"{exchange}-dead",
        } if use_dead_ex else {}
        self.__channel.queue_declare(
            queue=queue,
            durable=durable,
            arguments=arguments,
        )
        self.__channel.queue_bind(
            queue=queue,
            exchange=exchange,
            routing_key='',
        )
        self.__channel.basic_consume(
            queue=queue,
            on_message_callback=func,
        )

        self.__thread = Thread(target=self._thread_run)
        self.__thread.start()

    def _thread_run(self) -> None:
        try:
            self.__channel.start_consuming()
        except KeyboardInterrupt:
            self.__channel.stop_consuming()
        self.__connection.close()

    def publish(
            self,
            exchange: str,
            message: str,
            use_dead_ex: Optional[bool] = True,
            exchange_type: str = 'fanout',
    ) -> None:
        self.__connect()

        if use_dead_ex:
            self.__channel.exchange_declare(
                exchange=f"{exchange}-dead",
                exchange_type=exchange_type,
                durable=True,
            )

        self.__channel.exchange_declare(
            exchange=exchange,
            exchange_type=exchange_type,
            durable=True,
        )

        self.__channel.basic_publish(
            exchange=exchange,
            routing_key='',
            body=message,
        )
