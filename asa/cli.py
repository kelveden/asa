import argparse
import os
import colorama

from .config import config
from .commands import who, workspaces, teams

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
    who_parser = command_parser.add_parser("who", help="Identity the specified current user")
    who_parser.add_argument("-u", "--user", default="me", help="The user id")
    who_parser.set_defaults(func=who)

    #
    # asa workspaces
    #
    workspaces_parser = command_parser.add_parser("workspaces", help="List workspaces available to the user")
    workspaces_parser.add_argument("-u", "--user", default="me", help="The user id")
    workspaces_parser.set_defaults(func=workspaces)

    #
    # asa teams
    #
    teams_parser = command_parser.add_parser("teams", help="List the teams the user is on")
    teams_parser.add_argument("-u", "--user", default="me", help="The user id")
    teams_parser.add_argument("-w", "--workspace", default=config["defaults"]["DefaultWorkspace"], help="The workspace id")
    teams_parser.set_defaults(func=teams)

    args = parser.parse_args()

    #
    # Execute command
    #
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
