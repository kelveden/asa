from typing import Sequence, Iterable

from .asana import Asana
from colorama import Fore
from tabulate import tabulate

from term_image import image

from .config import get_board_config, to_team_id

LINE_SEPARATOR = "--------------------------------------"

def _new_asana_client(args):
    return Asana(args.token, args.verbose)

def _print_table(iterable: Iterable[Iterable], headers: Sequence[str] = []):
    print(tabulate(iterable,
                   headers=[f"{Fore.CYAN}{h}{Fore.RESET}" for h in headers],
                   tablefmt="heavy_grid",
                   numalign="left"))


def who(args):
    """
    Prints basic details of the user currently being used for authentication to Asana.

    :param args:
        open: Whether to bypass CLI output and just open the user details page in the browser.
    """
    asana = _new_asana_client(args)
    data = asana.get_user(user_id=args.user)

    _print_table([
        [f"{Fore.CYAN}Name:{Fore.RESET} {data['name']}"],
        [f"{Fore.CYAN}Id:{Fore.RESET}   {data['gid']}"]
    ])

    print(image.from_url(data['photo']['image_128x128'], width=30))


def workspaces(args):
    """
    Lists all the workspaces that the user has access to.
    """

    asana = _new_asana_client(args)
    data = asana.get_workspaces(user_id=args.user)

    workspace_list = [[item["workspace"]["gid"], item["workspace"]["name"]] for item in data]

    _print_table(workspace_list, headers=["Id", "Name"])


def teams(args):
    """
    Lists all the teams that the user is on.
    """
    asana = _new_asana_client(args)
    data = asana.get_teams(workspace=args.workspace, user_id=args.user)

    team_list = [[item["gid"], item["name"]] for item in data]

    _print_table(team_list, headers=["Id", "Name"])


def team(args):
    """
    Get membership details for the specified team
    """
    asana = _new_asana_client(args)
    team_id = to_team_id(args.team)

    data = asana.get_team(team_id=team_id)

    member_list = [[item["user"]["gid"], item["user"]["name"]] for item in data]

    if len(member_list) > 0:
        _print_table([
            [f"{Fore.CYAN}Name:{Fore.RESET} {data[0]["team"]["name"]}"],
        ])

        _print_table(member_list, headers=["Id", "Name"])


def boards(args):
    """
    List the boards belonging to the specified team
    """
    asana = _new_asana_client(args)
    team_id = to_team_id(args.team)

    data = asana.get_projects_by_team(team_id=team_id)

    project_list = [[item["gid"], item["name"]] for item in data]

    _print_table(project_list, headers=["Id", "Name"])


def board(args):
    """
    Print details of the specified board
    """

    asana = _new_asana_client(args)

    board_config = get_board_config(args.board)
    data = asana.get_incomplete_tasks(project_id=board_config["Id"])

    columns = board_config["Columns"].split(",")

    def _print_task(task):
        print(f"{task["name"]} - {task["assignee"]["name"] if task["assignee"] else "N/A"}")

    def _filter_tasks_by_column(column: str):
        yield [t for t in data
                if any(m["section"]["gid"] == column for m in t["memberships"])]

    tasks_by_column = [_filter_tasks_by_column(column) for column in columns]

    for tbc in tasks_by_column:
        print(LINE_SEPARATOR)
        for t in next(tbc): _print_task(t)
