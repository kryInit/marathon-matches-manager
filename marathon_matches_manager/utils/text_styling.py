from colorama import Style


def text_styling(msg: str, color: str = "", background: str = "", style: str = "") -> str:
    return f"{color}{background}{style}{msg}{Style.RESET_ALL}"
