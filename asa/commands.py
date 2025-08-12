import os
import re
from typing import Sequence, Iterable, List, Dict

from asa.asana.client import AsanaClient
from colorama import Fore

from .asana.model import NamedRef, Task, SectionCompact
from .config import (
    get_board_config,
    to_team_id,
    get_workspace,
    initialise_config,
    get_default_board,
    get_default_team,
    get_all_boards,
    get_all_teams,
    CONFIG_FILE_PATH,
    reload_config,
)


def _new_asana_client(args) -> AsanaClient:
    return AsanaClient(args.token, args.verbose)


def _print_named_refs(refs: Iterable[NamedRef]):
    for ref in refs:
        print(
            f"{ref.gid} {_to_link(ref.permalink_url, ref.name) if ref.permalink_url else ref.name}"
        )


def _to_link(url: str, label: str) -> str:
    # See https://stackoverflow.com/a/71309268
    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    escape_mask = "\033]8;;{}\033\\{}\033]8;;\033\\"

    return escape_mask.format(url, label)


def _print_tasks(tasks: List[Task], *, section_id_allowlist: Sequence[str] = ()):
    def _group_tasks_by_section(tasks_: Iterable[Task]) -> Dict[SectionCompact, List[Task]]:
        accumulated: Dict[SectionCompact, List[Task]] = {}

        for task_ in tasks_:
            sections = [
                tm.section for tm in task_.memberships if isinstance(tm, Task.SectionMembership)
            ]  # type: ignore
            for section_ in sections:
                if section_ in accumulated:
                    accumulated[section_].append(task_)
                else:
                    accumulated[section_] = [task_]

        return accumulated

    def _to_initials(name: str):
        return re.sub("[a-z ]", "", name)[:2]

    for section, tasks in reversed(list(_group_tasks_by_section(tasks).items())):
        if (len(section_id_allowlist) == 0) or (section.gid in section_id_allowlist):
            print(f"{Fore.CYAN}{section.name}{Fore.RESET}")

            for task_ in tasks:
                print(
                    f"  [{_to_initials(task_.assignee.name) if task_.assignee else '--'}] {_to_link(str(task_.permalink_url), task_.name)}"
                )


def me(args):
    """
    Prints basic details of the tasks assigned to the current user

    :param args:
        open: Whether to bypass CLI output and just open the user details page in the browser.
    """
    asana = _new_asana_client(args)
    task_list = asana.get_user_task_list(workspace=args.workspace, user_id="me")

    task_list_id = task_list.gid
    tasks = asana.get_user_incomplete_tasks(task_list_id=task_list_id)

    if args.open:
        for task in tasks:
            os.system(f"open {task.permalink_url}")
    else:
        _print_tasks(tasks)


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
        workspace = get_workspace()
        os.system(f"open https://app.asana.com/1/{workspace}/project/{board_config['Id']}")
    else:
        tasks = asana.get_project_incomplete_tasks(project_id=board_config["Id"])
        columns_str = board_config.get("Columns", fallback=None)
        columns = columns_str.split(",") if columns_str else []

        _print_tasks(tasks, section_id_allowlist=columns)


def search_tasks(args):
    """
    Execute a text search for tasks.
    """
    asana = _new_asana_client(args)

    board_id = get_board_config(args.board)["Id"]

    tasks = asana.search_tasks(
        workspace_id=get_workspace(), search_text=args.text, project_id=board_id
    )

    _print_tasks(tasks)


def manage_config(args) -> None:
    """
    Manage the asa configuration file.
    """
    asana = _new_asana_client(args)
    config_file_path = os.path.expanduser(CONFIG_FILE_PATH)

    if args.init:
        print(f"==> Preparing configuration to write to {CONFIG_FILE_PATH}...")
        initialise_config(asana=asana, config_file_path=config_file_path)

    reload_config()

    print(f"==> Generated from the config file {config_file_path}")

    default_board = get_default_board()
    default_team = get_default_team()
    all_boards = get_all_boards()
    all_teams = get_all_teams()

    print(f"{Fore.CYAN}Teams:{Fore.RESET}")
    for t in all_teams:
        print(f"  {t}{' [default]' if t == default_team else ''}")
    print(f"{Fore.CYAN}Boards:{Fore.RESET}")
    for b in all_boards:
        print(f"  {b}{' [default]' if b == default_board else ''}")
