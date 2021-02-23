from gwt_mts_parse.MtsVats import VATS
import pika
import json
import time
import re
from models.models import Trunk
from config.conf import RABBIT_HOST, RABBIT_PORT, RABBIT_QUEUE, LOG_NAME, TIMEOUT_REQUEST, conf_parser
from app.log_init import log_on

logger = log_on(LOG_NAME)
DATA_ACCESS = conf_parser('config/contracts.yaml')


def smart_timeout(attempts):
    if attempts <= 10:
        return time.sleep(10)
    else:
        return time.sleep(60)


def connect_rabbit_queue(fn):
    def wrapped():
        attempts = 0
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT))
                channel = connection.channel()
                logger.debug(f'Connect to RabbitMQ address: {RABBIT_HOST}')
                attempts = 0
                break
            except:
                logger.error(f'RabbitMQ CONNECTION ERROR: {RABBIT_HOST}')
                smart_timeout(attempts)
                attempts += 1

        channel.queue_declare(queue=RABBIT_QUEUE)
        logger.debug(f'Queue select: {RABBIT_QUEUE}')
        fn(channel)
        connection.close()

    return wrapped


@connect_rabbit_queue
def request_api(channel):
    for obj in DATA_ACCESS:
        logger.info(f" Request to object: {obj['obj']} - provider: {obj['provider']}")
        vats = VATS(address=obj['address'],
                    user=obj['login'],
                    password=obj['password'],
                    contract_url_abonents=obj['contract_url_abonents'])

        trunks = vats.get_trunks()

        for phone, trunk in trunks.items():
            send_trunk = Trunk(provider=obj['provider'],
                               obj=obj['obj'],
                               trunk_username=trunk['trunk_login'],
                               trunk_password=trunk['trunk_password'],
                               phone=phone,
                               attributes={'sip_device': trunk['trunk_sip_device'],
                                           'sip_enabled': trunk['trunk_sip_enabled'],
                                           'trunk_identify_line': trunk['trunk_identify_line']},
                               lines=int(obj['lines']))

            message = json.dumps(send_trunk.__dict__)
            channel.basic_publish(exchange='', routing_key=RABBIT_QUEUE, body=message)
            logger.info(f'Send trunk: {send_trunk.phone} queue: {RABBIT_QUEUE}')


def app_run():
    while True:
        request_api()
        time.sleep(TIMEOUT_REQUEST)
