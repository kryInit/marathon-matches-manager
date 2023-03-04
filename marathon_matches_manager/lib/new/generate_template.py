import logging
import shutil
from pathlib import Path

from colorama import Fore, Style

from ..utils import text_styling
from .ask_relate_contest import ask_related_contest


def generate_template(name: str,exists: bool) -> None:
    styled_name = text_styling(name, color=Fore.CYAN, style=Style.BRIGHT)
    logger = logging.getLogger(__name__)
    logger.info(f"start generating template as '{styled_name}'")

    path = Path.cwd().joinpath(name)

    if Path.exists(path) and not exists:
        logger.error(f"a directory named '{styled_name}' is already exists.")
        return

    if not Path.exists(path) and exists:
        logger.error(f"a directory named '{styled_name}' is not exists.")
        return
    
    if not exists:
        path.mkdir()
    # path.joinpath(".m3").mkdir()
    path.joinpath("m3-config.toml").touch()

    try:
        related_contest = ask_related_contest(name)
    except KeyboardInterrupt:
        print("\n")
        logger.info(text_styling("    -> Keyboard Interrupted", color=Fore.RED))
        logger.info(text_styling("       cleaning...", color=Fore.RED))
        shutil.rmtree(path)
        logger.info(text_styling("       cleaned", color=Fore.RED))
        return

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))
