import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.config/asa/config.ini"))
