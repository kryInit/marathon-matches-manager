import logging
import shutil
from pathlib import Path

import toml
import json
from colorama import Fore, Style

from ..utils import text_styling
from .ask_relate_contest import ask_related_contest
from .generate_project_config import generate_project_config


def generate_template(name: str) -> None:
    styled_name = text_styling(name, color=Fore.CYAN, style=Style.BRIGHT)
    logger = logging.getLogger(__name__)
    logger.info(f"start generating template as '{styled_name}'")

    project_root_path = Path.cwd().joinpath(name)

    if project_root_path.exists():
        logger.error(f"a directory named '{styled_name}' is already exists.")
        return

    project_root_path.mkdir()
    # path.joinpath(".m3").mkdir()
    project_root_path.joinpath("m3-config.toml").touch()

    try:
        related_contest = ask_related_contest(name)
    except KeyboardInterrupt:
        print("\n")
        logger.info(text_styling("    -> Keyboard Interrupted", color=Fore.RED))
        logger.info(text_styling("       cleaning...", color=Fore.RED))
        shutil.rmtree(project_root_path)
        logger.info(text_styling("       cleaned", color=Fore.RED))
        return

    project_config = generate_project_config(name, related_contest)

    config_file_path = project_root_path.joinpath("m3-config.toml")
    toml.dump(json.loads(project_config.json()), open(config_file_path, mode="w"))

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))
