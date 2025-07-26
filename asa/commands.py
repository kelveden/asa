import webbrowser
from math import floor, ceil
from typing import Sequence, Iterable, List, Dict

from asa.asana.client import AsanaClient
from colorama import Fore
from tabulate import tabulate

from term_image import image  # type: ignore

from .asana.model import NamedRef, Task, SectionCompact
from .config import get_board_config, to_team_id, DEFAULT_WORKSPACE

LINE_SEPARATOR = "-"
SECTION_SEPARATOR_LENGTH = 60


def _new_asana_client(args) -> AsanaClient:
    return AsanaClient(args.token, args.verbose)


def _print_table(rows: Iterable[Iterable], headers: Sequence[str] = ()):
    print(
        tabulate(
            rows,
            headers=[f"{Fore.CYAN}{h}{Fore.RESET}" for h in headers],
            tablefmt="heavy_grid",
            numalign="left",
        )
    )


def _print_named_refs(refs: Iterable[NamedRef]):
    _print_table([(ref.gid, ref.name) for ref in refs], headers=["Id", "Name"])


def _group_tasks_by_section(tasks: Iterable[Task]) -> Dict[SectionCompact, List[Task]]:
    accumulated: Dict[SectionCompact, List[Task]] = {}

    for task in tasks:
        sections = [tm.section for tm in task.memberships if isinstance(tm, Task.SectionMembership)]  # type: ignore
        for section in sections:
            if section in accumulated:
                accumulated[section].append(task)
            else:
                accumulated[section] = [task]

    return accumulated


def _print_tasks(tasks: List[Task], *, section_id_allowlist: Sequence[str] = ()):
    def _task_link(task_: Task):
        # See https://stackoverflow.com/a/71309268
        # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
        escape_mask = "\033]8;;{}\033\\{}\033]8;;\033\\"

        return escape_mask.format(task.permalink_url, task_.name)

    def _print_section_header(section_name: str):
        padding_length = (SECTION_SEPARATOR_LENGTH - len(section_name) - 2) / 2
        print(
            f"{LINE_SEPARATOR * floor(padding_length)} {section_name} {LINE_SEPARATOR * ceil(padding_length)}"
        )

    for section, tasks in _group_tasks_by_section(tasks).items():
        if (len(section_id_allowlist) == 0) or (section.gid in section_id_allowlist):
            _print_section_header(section.name)
            for task in tasks:
                print(f"{_task_link(task)} [{task.assignee.name if task.assignee else 'N/A'}]")


def who(args):
    """
    Prints basic details of the user currently being used for authentication to Asana.
    """
    asana = _new_asana_client(args)
    user = asana.get_user(user_id=args.user)

    _print_table(
        [
            [f"{Fore.CYAN}Name:{Fore.RESET} {user.name}"],
            [f"{Fore.CYAN}Id:{Fore.RESET}   {user.gid}"],
        ]
    )

    print(image.from_url(user.photo.image_128x128, width=30))


def me(args):
    """
    Prints basic details of the tasks assigned to the current user

    :param args:
        open: Whether to bypass CLI output and just open the user details page in the browser.
    """
    asana = _new_asana_client(args)
    task_list = asana.get_user_task_list(workspace=args.workspace, user_id=args.user)

    if args.open:
        webbrowser.open(f"https://app.asana.com/1/{args.workspace}/home", autoraise=True)
    else:
        task_list_id = task_list.gid
        tasks = asana.get_user_incomplete_tasks(task_list_id=task_list_id)

        _print_tasks(tasks)


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
        webbrowser.open(
            f"https://app.asana.com/1/{workspace}/project/{board_config['Id']}", autoraise=True
        )
    else:
        tasks = asana.get_project_incomplete_tasks(project_id=board_config["Id"])
        columns = board_config.get("Columns", fallback="").split(",")

        _print_tasks(tasks, section_id_allowlist=columns)
