import os
import configparser
from flask import json

class FlaskConfig:
    def __init__(self) -> None:
        config_path = f"./serverbase.cfg"

    def parse_config(path):
        if not os.path.isfile(path):
            pass


