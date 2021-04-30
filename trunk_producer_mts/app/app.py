import json
import time

from conf import RABBIT_QUEUE, LOG_NAME, TIMEOUT_REQUEST, DATA_ACCESS, \
    RABBIT_EXCHANGE
from gwt_mts_parse.MtsVats import VATS
from trunk_producer_mts.app.consumer import RMQConsumer
from trunk_producer_mts.app.log_init import log_on
from trunk_producer_mts.models.models import Trunk

logger = log_on(LOG_NAME)
rmq = RMQConsumer()


def smart_timeout(attempts):
    if attempts <= 10:
        return time.sleep(10)
    else:
        return time.sleep(60)


def request_api():
    for obj in DATA_ACCESS:
        logger.info(
            f" Request to object: {obj['obj']} - provider: {obj['provider']}")
        vats = VATS(address=obj['address'],
                    user=obj['login'],
                    password=obj['password'],
                    contract_url_abonents=obj['contract_url_abonents'])
        try:
            trunks = vats.get_trunks()
        except TypeError:
            logger.error("Connection error!")
            break

        for phone, trunk in trunks.items():
            send_trunk = Trunk(provider=obj['provider'],
                               obj=obj['obj'],
                               trunk_name=trunk['trunk_identify_line'],
                               trunk_username=trunk['trunk_login'],
                               trunk_password=trunk['trunk_password'],
                               phone=phone,
                               attributes={
                                   'sip_device': trunk['trunk_sip_device'],
                                   'sip_enabled': trunk['trunk_sip_enabled']},
                               lines=int(obj['lines']))

            message = json.dumps(send_trunk.__dict__)
            rmq.publish(RABBIT_EXCHANGE, message)
            logger.info(
                f'Send trunk: {send_trunk.phone} queue: {RABBIT_QUEUE}')


def app_run():
    while True:
        request_api()
        time.sleep(TIMEOUT_REQUEST)
