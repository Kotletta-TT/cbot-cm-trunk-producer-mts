import argparse

import pandas as pd

from gwt_mts_parse.MtsVats import VATS
from cli.utils.logger import init_logger
from cli.utils.arg_parse import arg_parse

"""
This CLI-interface make to automatization activates multiple trunks in MTS 
VATS.

It can also display all/activate/deactivate trunks, use flag -l to disable
the output to the screen and upload Excel file use flag -f.

Flag --filter allows display or save to Excel file all/activate/deactivate 
trunks.

Flag --action activate/deactivate multiple trunks only works flag --nums or 
arguments:
    * a (activate all inactive trunks in account)
    * d (deactivate all active trunks in account)

    --nums flag higher priority than these arguments, if use both flags,
    arguments --action flags will be ignored.

Flag --nums accepts a list of arguments format, if not flag --action,
    Then it will display detailed on the trunks info on the screen:
    --nums "79999999999
            78888888888
            7xxxxxxxxxx"
    or
    --nums "79999999999 78888888888 7xxxxxxxxxx"

Flag -v filter display/upload to current view, options pass to arguments:
    all
    phone
    login
    password
    sip_device
    sip_enabled
    identify_line
    
    format: -v phone login password sip_device sip_enabled

By default flags:
    # -f (file) *None [filename]
        * Flag upload to Excel file, when calling to no arg, will be have
        filename next format:
            trunks_(timestamp).xlsx.
    # -l
    # -v *all
    # --filter [*all|activate|deactivate]
    # --action *None
    # --nums *None


How it works:
    # Calling this script with necessary parameters "--login" and needed flags
    # Parse config and attempts find login
    # Authorisation on MTS VATS and parse data or manipulate trunks, depends
    on current use flags.
"""


def run():
    logger = init_logger('CLI')
    cli_data = arg_parse()
    print('test run func')

# if args.nums:
#     nums = args.nums.split('\n')
#
# vats = VATS(args.url, args.login, args.password, args.gwt_id)
#
# trunks = vats.get_trunks()
#
# dict_to_write = {"line": [],
#                  "authname": [],
#                  "password": []}
#
# phone_num = []
#
# for key, value in trunks.items():
#     phone_num.append(key)
#     dict_to_write['line'].append(value['trunk_identify_line'])
#     dict_to_write['authname'].append(value['trunk_login'])
#     dict_to_write['password'].append(value['trunk_password'])
#
# df = pd.DataFrame(dict_to_write)
# timestamp = datetime.strftime(datetime.now(), format="%Y-%m-%d_%H-%M")
# filename = f'vats_{timestamp}.xlsx'
#
# df.to_excel(filename, sheet_name='list_vats', index=False)

# vats.trunk_list_action(phone_num, 'add')
