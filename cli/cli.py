from cli.models.models import CliData, Config, Trunk
from cli.utils.arg_parse import arg_parse
from cli.utils.config_loader import parse_config
from gwt_mts_parse.MtsVats import VATS
from typing import Dict, List

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
                identify_line=v['identify_line']
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
        action(trunks, cli_data)


def display_view(trunks, cli_data):
    pass


def upload_to_file(trunks, cli_data):
    pass


def action(trunks, cli_data):
    pass




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
