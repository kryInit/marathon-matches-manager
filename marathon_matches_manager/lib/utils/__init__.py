import os
import shutil
from pathlib import Path
from typing import TypeVar, Union

from .gen_seeds import gen_seeds


def remove_any_file(path: Path) -> bool:
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    elif os.path.isfile(path):
        os.remove(path)
        return True
    else:
        return False


T = TypeVar("T", str, Path)


def expand_env_variables(s: T) -> T:
    is_path = False
    if isinstance(s, Path):
        s = str(s)
        is_path = True

    # todo: 例外処理入れた方が良い気がする
    while s != os.path.expandvars(s):
        s = os.path.expandvars(s)
    return Path(s) if is_path else s
