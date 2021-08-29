import argparse
import re
from datetime import datetime

from cli.models.models import CliData, PHONE, LOGIN, PASSWORD, SIP_DEVICE, \
    SIP_ENABLED, IDENTIFY_LINE
from cli.utils.help_message import *

CHOICE_FILTER = ['all', 'activate', 'deactivate']
CHOICE_ACTION = ['a', 'd']
CHOICE_VIEW = [PHONE, LOGIN, PASSWORD, SIP_DEVICE, SIP_ENABLED, IDENTIFY_LINE]


class NumsAction(argparse.Action):
    """
    A class for extended handler input nums, it converts bash-string
    separated by spaces or \n in the list.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(NumsAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, re.split('\n| ', values))


def arg_parse() -> CliData:
    time_fmt = "%Y-%m-%d_%H-%M"
    timestamp = datetime.strftime(datetime.now(), format=time_fmt)
    filename = f'vats_{timestamp}.xlsx'

    arg_engine = argparse.ArgumentParser(prog='cli')
    arg_engine.add_argument("-f",
                            type=str,
                            nargs='?',
                            const=filename,
                            default=None,
                            dest='filename',
                            help=HELP_F)
    arg_engine.add_argument("-l",
                            action="store_false",
                            dest='display',
                            help=HELP_L)
    arg_engine.add_argument("-v",
                            type=str,
                            nargs='+',
                            help=HELP_V,
                            default=['all', ],
                            dest='view',
                            choices=CHOICE_VIEW)
    arg_engine.add_argument("--action",
                            type=str,
                            nargs='+',
                            default=None,
                            dest='action',
                            choices=CHOICE_ACTION,
                            help=HELP_ACTION)
    arg_engine.add_argument("--login",
                            type=str,
                            dest='login',
                            required=True,
                            help=HELP_LOGIN)
    arg_engine.add_argument("--nums",
                            type=str,
                            nargs='+',
                            dest="nums",
                            action=NumsAction,
                            help=HELP_NUMS)
    arg_engine.add_argument("--filter",
                            nargs='?',
                            default='all',
                            dest='filter',
                            choices=CHOICE_FILTER,
                            help=HELP_FILTER)
    args = arg_engine.parse_args()
    cli_data = CliData(**vars(args))
    return cli_data
