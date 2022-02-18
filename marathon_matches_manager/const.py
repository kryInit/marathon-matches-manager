import dataclasses
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class _CONST:
    GLOBAL_CONFIG_DIRECTORY = f"{Path.home()}/.m3"
    GLOBAL_CONFIG_FILE = f"{GLOBAL_CONFIG_DIRECTORY}/config.toml"
    ATCODER_CONTESTS_URL = "https://atcoder.jp/contests/"
    ATCODER_PAST_MARATHON_CONTESTS_URL = "https://atcoder.jp/contests/archive?ratedType=0&category=1200"


CONST = _CONST()
