import csv
import argparse
from prettytable import PrettyTable
from gwt_mts_parse.MtsVats import VATS

parser = argparse.ArgumentParser(description='Add/Activate trunk SIP-Device in MTS VATS')
parser.add_argument('login', type=str, help='Login format +7-9XXXXXXXXXX')
parser.add_argument('password', type=str, help='Password VATS MTS')
parser.add_argument('url', type=str, help='URL: This inner link, how search them, you read to the docs')
parser.add_argument('action', type=str, help='list, add, del')
parser.add_argument('--sortby', type=str, default='Identify Line')
parser.add_argument('--filter', type=str, default='')
parser.add_argument('--file', type=argparse.FileType('w', encoding='UTF-8'), help='Write output to csv-file')
parser.add_argument('--all', action="store_true", default=False, help='Add and activate all off-SIP-device in account')
# parser.add_argument('--')

argcmd = parser.parse_args()

sim_list = []
login = argcmd.login
password = argcmd.password
url = 'vpbx.mts.ru'
contract_url_abonents = argcmd.url

vats = VATS(url, login, password, contract_url_abonents)
all_trunks = vats.get_trunks()
table = PrettyTable()


def write_to_csv(data_rows):
    with argcmd.file as file:
        trunk_writer = csv.writer(file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        trunk_writer.writerows(data_rows)





def get_list_table(sortby='Identify Line', filter=''):
    writer_list = []
    num = 0
    table.field_names = ['Identify Line', 'Login', 'Password', 'SIP-Device', 'Active', 'Inner-Link']
    for key, value in all_trunks.items():
        if filter == 'active=true':
            if value['trunk_sip_enabled']:
                row = [value['trunk_identify_line'], value['trunk_login'], value['trunk_password'],
                    value['trunk_sip_device'], value['trunk_sip_enabled'], value['trunk_inner_link']]
                table.add_row(row)
                num += 1
                writer_list.append(row)

        if filter == 'active=false':
            if not value['trunk_sip_enabled']:
                row = [value['trunk_identify_line'], value['trunk_login'], value['trunk_password'],
                       value['trunk_sip_device'], value['trunk_sip_enabled'], value['trunk_inner_link']]
                table.add_row(row)
                num += 1
                writer_list.append(row)

        if filter == '':
            row = [value['trunk_identify_line'], value['trunk_login'], value['trunk_password'],
                   value['trunk_sip_device'], value['trunk_sip_enabled'], value['trunk_inner_link']]
            table.add_row(row)
            num += 1
            writer_list.append(row)


    if argcmd.file:
        write_to_csv(writer_list)

    table.sortby = sortby
    print(table)
    print(f'Count rows {num}')


def add_device(sim_list):
    pass

if argcmd.action == 'list':
    get_list_table(argcmd.sortby, argcmd.filter)

if argcmd.action == 'add':
    add_device(sim_list)