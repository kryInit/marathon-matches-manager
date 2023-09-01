from colorama import Style

from ..utils import expand_env_variables
from .const import CONST
from .environment import environment


def text_styling(msg: str, color: str = "", background: str = "", style: str = "") -> str:
    return f"{color}{background}{style}{msg}{Style.RESET_ALL}"
