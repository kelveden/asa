import webbrowser
from typing import Sequence, Iterable

from asa.asana.client import AsanaClient
from colorama import Fore
from tabulate import tabulate

from term_image import image  # type: ignore

from .asana.model import NamedRef
from .config import get_board_config, to_team_id, DEFAULT_WORKSPACE

LINE_SEPARATOR = "--------------------------------------"

def _new_asana_client(args) -> AsanaClient:
    return AsanaClient(args.token, args.verbose)

def _print_table(rows: Iterable[Iterable], headers: Sequence[str] = ()):
    print(tabulate(rows,
                   headers=[f"{Fore.CYAN}{h}{Fore.RESET}" for h in headers],
                   tablefmt="heavy_grid",
                   numalign="left"))

def _print_named_refs(refs: Iterable[NamedRef]):
    _print_table([(ref.gid, ref.name) for ref in refs], headers=["Id", "Name"])


def who(args):
    """
    Prints basic details of the user currently being used for authentication to Asana.
    """
    asana = _new_asana_client(args)
    user = asana.get_user(user_id=args.user)

    _print_table([
        [f"{Fore.CYAN}Name:{Fore.RESET} {user.name}"],
        [f"{Fore.CYAN}Id:{Fore.RESET}   {user.gid}"]
    ])

    print(image.from_url(user.photo.image_128x128, width=30))

def me(args):
    """
    Prints basic details of the tasks assigned to the current user

    :param args:
        open: Whether to bypass CLI output and just open the user details page in the browser.
    """
    asana = _new_asana_client(args)
    task_list = asana.get_user_tasks(workspace=args.workspace, user_id=args.user)

    if args.open:
        webbrowser.open(f"https://app.asana.com/1/{args.workspace}/home", autoraise=True)
    else:
        print(task_list)

    #_print_table(workspace_list, headers=["Id", "Name"])


def workspaces(args):
    """
    Lists all the workspaces that the user has access to.
    """

    asana = _new_asana_client(args)
    workspaces_memberships = asana.get_workspace_memberships(user_id=args.user)

    _print_named_refs([wm.workspace for wm in workspaces_memberships])


def teams(args):
    """
    Lists all the teams that the user is on.
    """
    asana = _new_asana_client(args)
    teams_ = asana.get_teams(workspace=args.workspace, user_id=args.user)

    _print_named_refs(teams_)


def team(args):
    """
    Get membership details for the specified team
    """
    asana = _new_asana_client(args)
    team_id = to_team_id(args.team)

    team_memberships = asana.get_team_members(team_id=team_id)

    _print_named_refs([tm.user for tm in team_memberships])

def boards(args):
    """
    List the boards belonging to the specified team
    """
    asana = _new_asana_client(args)
    team_id = to_team_id(args.team)

    projects = asana.get_projects_by_team(team_id=team_id)
    _print_named_refs(projects)


def board(args):
    """
    Print details of the specified board
    """

    asana = _new_asana_client(args)

    board_config = get_board_config(args.board)

    if args.open:
        workspace = DEFAULT_WORKSPACE
        webbrowser.open(f"https://app.asana.com/1/{workspace}/project/{board_config["Id"]}", autoraise=True)
    else:
        data = asana.get_project_incomplete_tasks(project_id=board_config["Id"])

        columns = board_config.get("Columns", fallback="").split(",")

        def _print_task(task):
            print(f"{task["name"]} - {task["assignee"]["name"] if task["assignee"] else "N/A"}")

        def _filter_tasks_by_column(column: str):
            yield [task for task in data
                    if any(m["section"]["gid"] == column for m in task["memberships"])]

        tasks_by_column = [_filter_tasks_by_column(column) for column in columns] if len(columns) > 0 else data

        for tbc in tasks_by_column:
            print(LINE_SEPARATOR)
            for t in next(tbc):
                _print_task(t)
