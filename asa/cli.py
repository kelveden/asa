import argparse
import os
import colorama

from .config import config, DEFAULT_TEAM, DEFAULT_BOARD
from .commands import who, workspaces, teams, team, boards, board

colorama.init()


def execute_cli():
    # Parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get('ASANA_TOKEN'), help="Asana personal access token")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Whether to print details of requests and responses")

    command_parser = parser.add_subparsers(title="commands")

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

    #
    # asa team
    #
    team_parser = command_parser.add_parser("team", help="Get details for the specified team")
    team_parser.add_argument("-t", "--team", default=DEFAULT_TEAM, help="The team name from the asa configuration")
    team_parser.set_defaults(func=team)

    #
    # asa boards
    #
    boards_parser = command_parser.add_parser("boards", help="List the boards for the specified team")
    boards_parser.add_argument("-t", "--team", default=DEFAULT_TEAM, help="The team name from the asa configuration")
    boards_parser.set_defaults(func=boards)

    #
    # asa board
    #
    board_parser = command_parser.add_parser("board", help="Get the content for the specified board")
    board_parser.add_argument("-b", "--board", default=DEFAULT_BOARD, help="The board name from the asa configuration")
    board_parser.set_defaults(func=board)

    args = parser.parse_args()

    #
    # Execute command
    #
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
