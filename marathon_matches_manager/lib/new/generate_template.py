import logging
import shutil
from pathlib import Path

from colorama import Fore, Style

from ..utils import text_styling
from .ask_relate_contest import ask_related_contest
from .generate_m3_config import generate_m3_config

def generate_template(name: str,has_create: bool) -> None:
    styled_name = text_styling(name, color=Fore.CYAN, style=Style.BRIGHT)
    logger = logging.getLogger(__name__)
    logger.info(f"start generating template as '{styled_name}'")
    path = Path.cwd()
    if not has_create:
        path = path.joinpath(name)
        if path.exists():
            logger.error(f"a directory named '{styled_name}' is already exists.")
            return        
        path.mkdir()
    path = path.joinpath('m3-config.toml')
  
    # path.joinpath(".m3").mkdir()
    logger.info(path)
    try:
        related_contest = ask_related_contest(name)
        generate_m3_config(path,related_contest,name)
    except KeyboardInterrupt:
        print("\n")
        logger.info(text_styling("    -> Keyboard Interrupted", color=Fore.RED))
        logger.info(text_styling("       cleaning...", color=Fore.RED))
        shutil.rmtree(path)
        logger.info(text_styling("       cleaned", color=Fore.RED))
        return

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))
