import logging
from typing import List, Dict

import yaml

from cli.models.models import Config
from cli.utils.logger import init_logger


def parse_config(filename: str) -> List[Config] or None:
    logger: logging.Logger = init_logger('CLI-config')
    configs: List[Config] = []
    yaml_parse: Dict
    try:
        with open(filename, 'r') as f:
            yaml_parse = yaml.safe_load(f)
    except (FileNotFoundError, PermissionError) as e:
        logger.error(e)
        return None
    except yaml.YAMLError as e:
        logger.error(e)
        return None
    for account in yaml_parse['contracts']:
        try:
            configs.append(Config(
                address=account['address'],
                login=account['login'],
                password=account['password'],
                inner_id=account['contract_url_abonents']
            ))
        except ValueError as e:
            logger.error(e)
            return None
    return configs


# parse_config('lol')