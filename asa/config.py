import configparser
import os
from configparser import NoOptionError
from curses.ascii import isdigit

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.config/asa/config.ini"))

try:
    DEFAULT_TEAM = config['defaults']['DefaultTeam']
except NoOptionError:
    DEFAULT_TEAM = None

try:
    DEFAULT_BOARD = config['defaults']['DefaultBoard']
except NoOptionError:
    DEFAULT_BOARD = None

def _get_config_by_id(id: str, section_prefix: str):
    for s in config.sections():
        if s.startswith(f"{section_prefix}.") and config[s]["Id"] == id:
            yield config[s]

def get_board_config(board_name_or_id: str):
    if board_name_or_id.isdigit():
        return next(_get_config_by_id(board_name_or_id, "board"), None)
    else:
        return config[f"board.{board_name_or_id}"]

def get_team_config(team_name_or_id: str):
    if team_name_or_id.isdigit():
        return next(_get_config_by_id(team_name_or_id, "team"), None)
    else:
        return config[f"team.{team_name_or_id}"]

def _to_id(name_or_id: str, config_getter):
    if config_ := config_getter(name_or_id):
        return config_["Id"]
    else:
        return name_or_id

def to_team_id(team_name_or_id: str):
    return _to_id(team_name_or_id, get_team_config)

def to_board_id(board_name_or_id: str):
    return _to_id(board_name_or_id, get_board_config)