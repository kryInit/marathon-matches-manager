import logging
import os
from typing import List

from .const import CONST


def generate_template(name: str) -> None:
    # ディレクトリ作成
    # コンテストとの紐付け
    # testerの取得

    logger = logging.getLogger(__name__)
    logger.info(f"start generating template as '{name}'")

    if os.path.exists(name):
        logger.error(f"a directory named '{name}' is already exists.")
        return

    os.makedirs(name)

    predicted_contests_name = predict_related_contests(name)
    for pcn in predicted_contests_name:
        is_for_the_contest = input(f"\nthis template will be used for '{pcn}'?  [y/n]: ").strip() == "y"
        print()

    logger.info("creation successful!")


def predict_related_contests(name) -> List[str]:
    # name, url, period, in progress,
    logger = logging.getLogger(__name__)
    logger.debug(CONST.AtCoderContestsURL)

    return ["AtCoder Heuristic Contest 001"]


