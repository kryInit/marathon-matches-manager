import json
import os
import shutil
from pathlib import Path

import toml
from colorama import Fore, Style
from logzero import logger

from ..misc import CONST, environment, text_styling
from ..run import exec_command
from .ask_relate_contest import ask_related_contest
from .generate_project_config import generate_project_config


def generate_template(name: str, in_place: bool = False) -> None:
    styled_name = text_styling(name, color=Fore.CYAN, style=Style.BRIGHT)
    logger.info(f"start generating template as '{styled_name}'")

    project_root_path = Path.cwd() if in_place else Path.cwd().joinpath(name)

    # create directory
    if not in_place:
        if project_root_path.exists():
            logger.error(f"a directory named '{styled_name}' is already exists.")
            return
        project_root_path.mkdir()

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

    config_file_path = project_root_path.joinpath(CONST.CONFIG_FILE_NAME)
    toml.dump(json.loads(project_config.json(exclude_unset=True)), open(config_file_path, mode="w"))

    # append global config
    with open(config_file_path, mode="a") as writer:
        writer.write(
            (
                "\n[contest.environment]\n"
                "# official_visualizer_url = ...\n"
                "# official_tools_url = ...\n"
                '# official_tools_target = "gen vis tester"\n'
                'official_tools_target = "gen vis"\n\n'
            )
        )
        with open(CONST.GLOBAL_CONFIG_FILE_PATH) as reader:
            writer.write("\n#\n# following is a copy of the global config\n#\n\n")
            writer.write(reader.read())

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))

    os.environ["project_root_path"] = str(project_root_path)
    project_config.update_os_environment()

    if environment.global_config.initialize is not None:
        logger.info("exec initialize command...")
        environment.global_config.initialize.exec()
