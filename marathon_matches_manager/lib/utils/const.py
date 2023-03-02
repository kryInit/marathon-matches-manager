from pathlib import Path

from pydantic import BaseModel, HttpUrl, parse_obj_as


class Const(BaseModel):
    CONFIG_FILE_NAME: str = "m3-config.toml"
    GLOBAL_CONFIG_ROOT_PATH: Path = Path.home().joinpath(".m3")
    GLOBAL_CONFIG_FILE_PATH: Path = GLOBAL_CONFIG_ROOT_PATH.joinpath(CONFIG_FILE_NAME)
    ATCODER_URL: HttpUrl = parse_obj_as(HttpUrl, "https://atcoder.jp")
    ATCODER_CONTESTS_URL: HttpUrl = parse_obj_as(HttpUrl, "https://atcoder.jp/contests/")
    ATCODER_PAST_HEURISTIC_CONTESTS_URL: HttpUrl = parse_obj_as(
        HttpUrl, "https://atcoder.jp/contests/archive?ratedType=4"
    )

    class Config:
        allow_mutation = False


CONST = Const()
