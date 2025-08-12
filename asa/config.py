import configparser
import os
import pathlib
import re
from itertools import chain
from typing import List

import questionary

from asa.asana.client import AsanaClient
from asa.asana.model import NamedRef, Workspace, Team, Project, Section

CONFIG_FILE_DIR = "~/.config/asa"
CONFIG_FILE_PATH = f"{CONFIG_FILE_DIR}/config.ini"

config = configparser.ConfigParser()
config.read(os.path.expanduser(CONFIG_FILE_PATH))


#
# Config getters
#


def _get_config_by_id(id_: str, section_prefix: str):
    for s in config.sections():
        if s.startswith(f"{section_prefix}.") and config[s]["Id"] == id_:
            yield config[s]


def get_board_config(board_identifier: str):
    if board_identifier.isdigit():
        return next(_get_config_by_id(board_identifier, "board"), None)
    else:
        return config[f"board.{board_identifier}"]


def get_team_config(team_identifier: str):
    if team_identifier.isdigit():
        return next(_get_config_by_id(team_identifier, "team"), None)
    else:
        return config[f"team.{team_identifier}"]


def get_workspace() -> str | None:
    return config["defaults"]["DefaultWorkspace"] if config.has_section("defaults") else None


def get_default_team() -> str | None:
    return config["defaults"]["DefaultTeam"] if config.has_section("defaults") else None


def get_default_board() -> str | None:
    return config["defaults"]["DefaultBoard"] if config.has_section("defaults") else None


def get_all_boards() -> List[str]:
    section_names = config.sections()
    return [re.sub("^board\\.", "", s) for s in section_names if s.startswith("board.")]


def get_all_teams() -> List[str]:
    section_names = config.sections()
    return [re.sub("^team\\.", "", s) for s in section_names if s.startswith("team.")]


def reload_config():
    config.read(os.path.expanduser(CONFIG_FILE_PATH))


#
# Id converters
#


def _to_id(name_or_id: str, config_getter):
    if config_ := config_getter(name_or_id):
        return config_["Id"]
    else:
        return name_or_id


def to_team_id(team_name_or_id: str):
    return _to_id(team_name_or_id, get_team_config)


def to_board_id(board_name_or_id: str):
    return _to_id(board_name_or_id, get_board_config)


#
# Initialisation wizard
#


def initialise_config(*, asana: AsanaClient, config_file_path: str) -> None:
    """
    Creates a asa config file based on the choices selected via wizard.
    """

    def _choose_workspace() -> Workspace:
        workspaces = [wm.workspace for wm in asana.get_workspace_memberships(user_id="me")]

        choices = [questionary.Choice(w.name, w) for w in workspaces]
        default_choice = next((c for c in choices if c.value == get_workspace()), None)

        workspace_: Workspace = questionary.select(
            "Which workspace do you want asa to work with?", choices=choices, default=default_choice
        ).ask()

        return workspace_

    def _choose_teams(workspace_id: str) -> List[Team]:
        teams = asana.get_teams(workspace=workspace_id, user_id="me")

        return questionary.checkbox(
            "Which teams do you want asa to work with?",
            choices=[questionary.Choice(t.name, t) for t in teams],
        ).ask()

    def _choose_default_team(teams_: List[Team]) -> Team:
        return questionary.select(
            "Which team do you wish to be the default?",
            choices=[questionary.Choice(t.name, t) for t in teams_],
        ).ask()

    def _choose_projects(team: Team) -> List[Project]:
        projects_ = asana.get_projects_by_team(team_id=team.gid)

        if len(projects_) > 0:
            return questionary.checkbox(
                f"Team: '{team.name}': which boards do you want asa to work with?",
                choices=[questionary.Choice(p.name, p) for p in projects_],
            ).ask()
        else:
            return []

    def _choose_default_board(projects: List[Project]) -> Project:
        return questionary.select(
            "Which board do you wish to be the default?",
            choices=[questionary.Choice(p.name, p) for p in projects],
        ).ask()

    def _choose_sections(project: Project) -> List[Section]:
        sections_ = asana.get_sections_by_project(project_id=project.gid)

        return questionary.checkbox(
            f"Board: '{project.name}': which columns do you want asa to display for this board by default?",
            choices=[questionary.Choice(p.name, p) for p in sections_],
        ).ask()

    def _name_to_config_key(name: str):
        return re.sub("[^a-z_]", "", name.strip().lower().replace(" ", "_"))

    workspace: NamedRef = _choose_workspace()

    selected_teams: List[Team] = _choose_teams(workspace_id=workspace.gid)
    default_team: NamedRef = _choose_default_team(selected_teams)

    selected_projects: List[Project] = list(
        chain.from_iterable([_choose_projects(t) for t in selected_teams])
    )
    default_board = _choose_default_board(selected_projects)

    config_parser = configparser.ConfigParser()
    config_parser.optionxform = str  # type: ignore

    config_parser["defaults"] = {
        "DefaultWorkspace": workspace.gid,
        "DefaultTeam": _name_to_config_key(default_team.name),
        "DefaultBoard": _name_to_config_key(default_board.name),
    }

    for t in selected_teams:
        config_parser[f"team.{_name_to_config_key(t.name)}"] = {"Id": t.gid}

    for p in selected_projects:
        sections = _choose_sections(p)
        config_parser[f"board.{_name_to_config_key(p.name)}"] = {
            "Id": p.gid,
            "Columns": ",".join([s.gid for s in sections]),
        }

    os.makedirs(pathlib.Path(config_file_path).parent.resolve(), exist_ok=True)

    with open(config_file_path, "w") as config_file:
        config_parser.write(config_file)
