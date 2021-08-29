import sys
from typing import Dict, List

import pandas as pd

from cli.models.models import CliData, Config, Trunk, EXCEL_STRUCT
from cli.utils.arg_parse import arg_parse, CHOICE_VIEW
from cli.utils.config_loader import parse_config
from cli.utils.print_table import print_table
from gwt_mts_parse.MtsVats import VATS

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
    
    IMPORTANT: The quotation marks surrounding the list are needed!

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

ALL = CHOICE_VIEW


def get_conf(cli_data: CliData, filename: str) -> Config:
    configs = parse_config(filename)
    for conf in configs:
        if cli_data.login == conf.login:
            return conf
    raise ValueError(f'Login {cli_data.login} not found in config')


def check_nums_arg(trunks: Dict[str, Dict], nums: List[str]) -> List[Trunk]:
    find_trunks: List[Trunk] = []
    if nums:
        for num in nums:
            if num in trunks:
                trunk = Trunk(
                    phone=num,
                    login=trunks[num]['trunk_login'],
                    password=trunks[num]['trunk_password'],
                    sip_device=trunks[num]['trunk_sip_device'],
                    sip_enabled=trunks[num]['trunk_sip_enabled'],
                    identify_line=trunks[num]['trunk_inner_link']
                )
                find_trunks.append(trunk)
    else:
        for k, v in trunks.items():
            trunk = Trunk(
                phone=k,
                login=v['trunk_login'],
                password=v['trunk_password'],
                sip_device=v['trunk_sip_device'],
                sip_enabled=v['trunk_sip_enabled'],
                identify_line=v['trunk_identify_line']
            )
            find_trunks.append(trunk)
    return find_trunks


def run():
    cli_data = arg_parse()
    config = get_conf(cli_data, 'confs/prod/trunk_producer_mts.yaml')
    vats = VATS(config.address,
                config.login,
                config.password,
                config.inner_id)
    trunks = vats.get_trunks()
    trunks = check_nums_arg(trunks, cli_data.nums)
    if cli_data.display:
        display_view(trunks, cli_data)
    if cli_data.filename:
        upload_to_file(trunks, cli_data)
    if cli_data.action:
        action(vats, trunks, cli_data)
        trunks = vats.get_trunks()
        trunks = check_nums_arg(trunks, [])
        cli_data.filter = 'all'
        cli_data.view = ['all', ]
        user_input = input('For display result press "p" for save press "f" '
                           'exit press any key')
        if user_input.lower() == 'p':
            display_view(trunks, cli_data)
        elif user_input.lower() == 'f':
            upload_to_file(trunks, cli_data)
        else:
            sys.exit()


def get_filtered_list(trunks: List[Trunk], cli_data: CliData) -> List[Trunk]:
    if cli_data.filter == 'activate':
        return [trunk for trunk in trunks if trunk.sip_enabled]
    elif cli_data.filter == 'deactivate':
        return [trunk for trunk in trunks if not trunk.sip_enabled]
    else:
        return trunks


def get_view_list(cli_data: CliData) -> List[str]:
    if 'all' in cli_data.view:
        return ALL
    else:
        return cli_data.view


def get_upload_fields(cli_data: CliData) -> Dict[str, List]:
    if 'all' in cli_data.view:
        return EXCEL_STRUCT
    else:
        return {field: [] for field in cli_data.view}


def display_view(trunks: List[Trunk], cli_data: CliData):
    filter_trunks = get_filtered_list(trunks, cli_data)
    view_list = get_view_list(cli_data)
    print_table(view_list, filter_trunks)


def upload_to_file(trunks: List[Trunk], cli_data: CliData):
    filter_trunks = get_filtered_list(trunks, cli_data)
    upload_fields = get_upload_fields(cli_data)
    for field in upload_fields:
        upload_fields[field] = [trunk.dict()[field] for trunk in filter_trunks]
    df = pd.DataFrame(upload_fields)
    df.to_excel(cli_data.filename, sheet_name='list_vats', index=False)


def action(vats: VATS, trunks: List[Trunk], cli_data: CliData):
    if cli_data.action and cli_data.nums:
        vats.trunk_list_action(cli_data.nums, 'add')
    elif cli_data.action == 'a':
        vats.trunk_list_action(
            [trunk.phone for trunk in trunks if not trunk.sip_enabled], 'add')
    elif cli_data.action == 'd':
        vats.trunk_list_action(
            [trunk.phone for trunk in trunks if trunk.sip_enabled], 'del')

