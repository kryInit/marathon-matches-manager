import logging
import shutil
from pathlib import Path

from colorama import Fore, Style

from ..utils import text_styling
from .ask_relate_contest import ask_related_contest


def generate_template(name: str) -> None:
    styled_name = text_styling(name, color=Fore.CYAN, style=Style.BRIGHT)
    logger = logging.getLogger(__name__)
    logger.info(f"start generating template as '{styled_name}'")

    path = Path.cwd().joinpath(name)

    if Path.exists(path):
        logger.error(f"a directory named '{styled_name}' is already exists.")
        return

    path.mkdir()
    path.joinpath(".m3").mkdir()
    path.joinpath(".m3/test").mkdir()
    path.joinpath(".m3/tools").mkdir()
    path.joinpath(".m3/config.toml").mkdir()

    try:
        related_contest = ask_related_contest(name)
    except KeyboardInterrupt:
        print("\n")
        logger.info(text_styling("    -> Keyboard Interrupted", color=Fore.RED))
        logger.info(text_styling("       cleaning...", color=Fore.RED))
        shutil.rmtree(path)
        logger.info(text_styling("       cleaning finished", color=Fore.RED))
        return

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))
