import argparse
import os
import colorama

from .config import get_workspace, get_default_team, get_default_board
from .commands import teams, team, boards, board, me, manage_config, search_tasks

colorama.init()


def execute_cli():
    # Parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token", default=os.environ.get("ASANA_TOKEN"), help="Asana personal access token"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Whether to print details of requests and responses",
    )

    command_parser = parser.add_subparsers(title="commands")

    #
    # asa me
    #
    me_parser = command_parser.add_parser("me", help="Get incomplete tasks for the current user")
    me_parser.add_argument("-w", "--workspace", default=get_workspace(), help="The workspace id")
    me_parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        default=False,
        help="Open the tasks assigned to the current user in the default browser",
    )
    me_parser.set_defaults(func=me)

    #
    # asa teams
    #
    teams_parser = command_parser.add_parser("teams", help="List the teams the user is on")
    teams_parser.add_argument("-u", "--user", default="me", help="The user id")
    teams_parser.add_argument("-w", "--workspace", default=get_workspace(), help="The workspace id")
    teams_parser.set_defaults(func=teams)

    #
    # asa team
    #
    team_parser = command_parser.add_parser("team", help="Get details for the specified team")
    team_parser.add_argument(
        "-t",
        "--team",
        default=get_default_team(),
        help="The team identifier from the asa configuration",
    )
    team_parser.set_defaults(func=team)

    #
    # asa boards
    #
    boards_parser = command_parser.add_parser(
        "boards", help="List the boards for the specified team"
    )
    boards_parser.add_argument(
        "-t",
        "--team",
        default=get_default_team(),
        help="The team identifier from the asa configuration",
    )
    boards_parser.set_defaults(func=boards)

    #
    # asa board
    #
    board_parser = command_parser.add_parser(
        "board", help="Get the content for the specified board"
    )
    board_parser.add_argument(
        "-b",
        "--board",
        default=get_default_board(),
        help="The board identifier from the asa configuration",
    )
    board_parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        default=False,
        help="Open the board in the default browser",
    )
    board_parser.set_defaults(func=board)

    #
    # asa search
    #
    search_parser = command_parser.add_parser("search", help="Search for tasks")

    search_parser.add_argument(
        "text",
        help="The text to search for",
    )
    search_parser.add_argument(
        "-b",
        "--board",
        default=get_default_board(),
        help="The board identifier from the asa configuration to use as the target of the search",
    )
    search_parser.set_defaults(func=search_tasks)

    #
    # asa config
    #
    config_parser = command_parser.add_parser("config", help="Manage the asa configuration")

    config_parser.add_argument(
        "--init",
        action="store_true",
        default=False,
        help="Initialise a new configuration file",
    )
    config_parser.set_defaults(func=manage_config)

    args = parser.parse_args()

    #
    # Execute command
    #
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
