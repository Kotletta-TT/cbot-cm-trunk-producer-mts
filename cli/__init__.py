from cli.cli import run

def main():
    run()

# import argparse
# from datetime import datetime
#
# from cli.utils.help_message import *
#
#
# def main():
#     timestamp = datetime.strftime(datetime.now(), format="%Y-%m-%d_%H-%M")
#     filename = f'vats_{timestamp}.xlsx'
#
#     argEngine = argparse.ArgumentParser(prog='cli')
#     argEngine.add_argument("-f",
#                            type=str,
#                            nargs='?',
#                            const=filename,
#                            default=None,
#                            help=HELP_F)
#     argEngine.add_argument("-l",
#                            action="store_false",
#                            help=HELP_L)
#     argEngine.add_argument("-v",
#                            type=str,
#                            nargs='+',
#                            help=HELP_V,
#                            default='all',
#                            choices=['phone', 'burbone'])
#     argEngine.add_argument("--action",
#                            type=str,
#                            nargs='?',
#                            default=None,
#                            choices=['a', 'b', 'c'])
#     argEngine.add_argument("--login",
#                            type=str,
#                            help=HELP_LOGIN)
#     argEngine.add_argument("--nums",
#                            type=str,
#                            default=[],
#                            help=HELP_NUMS)
#     argEngine.add_argument("--filter",
#                            default='all',
#                            nargs='?',
#                            choices=['all', 'activate', 'deactivate'],
#                            help=HELP_FILTER)
#     args = argEngine.parse_args()
#     print(args.v)
#     cli_data = ''
#     return cli_data
