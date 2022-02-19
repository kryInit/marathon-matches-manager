from typing import Optional

from colorama import Back, Fore, Style


def text_styling(msg: str, color: str = "", background: str = "", style: str = "") -> str:
    return f"{color}{background}{style}{msg}{Fore.RESET}{Back.RESET}{Style.RESET_ALL}"
