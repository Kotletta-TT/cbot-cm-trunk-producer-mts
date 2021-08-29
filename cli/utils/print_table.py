from typing import List

from prettytable import PrettyTable

from cli.models.models import Trunk


def convert_trunk_to_view(view_list: List[str], trunk: Trunk) -> List[str]:
    result: List[str] = []
    for key, value in trunk.dict().items():
        if key in view_list:
            result.append(value)
    return result


def print_table(view_list: List[str], trunks: List[Trunk]):
    table = PrettyTable()
    table.field_names = view_list
    for trunk in trunks:
        table.add_row(convert_trunk_to_view(view_list, trunk))
    print(table)
    print(f'Count trunks: {len(trunks)}')
    print(f"Activated: "
          f"{len([trunk for trunk in trunks if trunk.sip_enabled])}")
    print(f"Deactivated: "
          f"{len([trunk for trunk in trunks if not trunk.sip_enabled])}")

