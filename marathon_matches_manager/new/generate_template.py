import logging
from pathlib import Path

from colorama import Fore, Style

from marathon_matches_manager.new.relate_contest import ask_related_contest
from marathon_matches_manager.utils.text_styling import text_styling


def generate_template(name: str) -> None:
    logger = logging.getLogger(__name__)
    logger.info(f"start generating template as '{name}'")

    path = Path.joinpath(Path.cwd(), name)

    if Path.exists(path):
        logger.error(f"a directory named '{name}' is already exists.")
        return

    Path.mkdir(path)
    Path.mkdir(Path.joinpath(path, "./.m3"))
    Path.mkdir(path.joinpath(path, "./.m3/test"))
    Path.mkdir(path.joinpath(path, "./.m3/tools"))
    Path.touch(path.joinpath(path, "./.m3/config.toml"))

    related_contest = ask_related_contest(name)

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))
