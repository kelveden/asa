import argparse
import os

import colorama

from .commands import who

colorama.init()


def execute_cli():
    # Parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get('ASANA_TOKEN'), help="Asana personal access token")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Whether to print details of requests and responses")

    command_parser = parser.add_subparsers(title="commands")

    #
    # asa me
    #
    # me_parser = command_parser.add_parser("me", help="Get my tasks")
    # me_parser.add_argument("-a", "--all", action="append", help="Include all tasks, including completed")
    # me_parser.set_defaults(func=me)

    #
    # asa who
    #
    who_parser = command_parser.add_parser("who", help="Identity the current user")
    who_parser.set_defaults(func=who)


    args = parser.parse_args()

    #
    # Execute command
    #
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
