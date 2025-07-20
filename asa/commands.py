from pprint import pprint
from typing import Sequence, Iterable

from .asana import Asana
from colorama import Fore
from tabulate import tabulate

from term_image import image

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