import argparse

import yaml


def conf_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        dest='config',
        type=str,
        default='confs/trunk_producer_mts.yaml')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        return yaml.safe_load(f)


conf = conf_parser()

RABBIT_HOST = conf['rmq']['host']
RABBIT_VHOST = conf['rmq']['vhost']
RABBIT_PORT = conf['rmq']['port']
RABBIT_USERNAME = conf['rmq']['username']
RABBIT_PASS = conf['rmq']['password']
RABBIT_QUEUE = conf['rmq']['queue']
RABBIT_EXCHANGE = conf['rmq']['exchange']
LOG_LEVEL = conf['log-level']
LOG_NAME = conf['log-name']
TIMEOUT_REQUEST = conf['timeout-request']

DATA_ACCESS = conf['contracts']
