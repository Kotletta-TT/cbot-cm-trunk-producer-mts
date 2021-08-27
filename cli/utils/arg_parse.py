import argparse
from datetime import datetime

from cli.models.models import CliData
from cli.utils.help_message import *

CHOICE_FILTER = ['all', 'activate', 'deactivate']
CHOICE_ACTION = ['a', 'd']
CHOICE_VIEW = ['phone', 'login', 'password', 'sip_device',
               'sip_enabled',
               'identify_line']


def arg_parse() -> CliData:
    time_fmt = "%Y-%m-%d_%H-%M"
    timestamp = datetime.strftime(datetime.now(), format=time_fmt)
    filename = f'vats_{timestamp}.xlsx'

    argEngine = argparse.ArgumentParser(prog='cli')
    argEngine.add_argument("-f",
                           type=str,
                           nargs='?',
                           const=filename,
                           default=None,
                           help=HELP_F)
    argEngine.add_argument("-l",
                           action="store_false",
                           help=HELP_L)
    argEngine.add_argument("-v",
                           type=str,
                           nargs='+',
                           help=HELP_V,
                           default='all',
                           choices=CHOICE_VIEW)
    argEngine.add_argument("--action",
                           type=str,
                           nargs='+',
                           choices=CHOICE_ACTION)
    argEngine.add_argument("--login",
                           type=str,
                           help=HELP_LOGIN)
    argEngine.add_argument("--nums",
                           type=str,
                           help=HELP_NUMS)
    argEngine.add_argument("--filter",
                           nargs='?',
                           default='all',
                           choices=CHOICE_FILTER,
                           help=HELP_FILTER)
    args = argEngine.parse_args()

    cli_data = CliData()
    return cli_data
