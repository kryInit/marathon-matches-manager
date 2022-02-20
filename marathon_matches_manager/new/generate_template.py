import dataclasses
import logging
import os
import re
import sys
from collections import OrderedDict
from typing import List, Optional

import Levenshtein
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style

from marathon_matches_manager.const import CONST
from marathon_matches_manager.utils.text_styling import text_styling


@dataclasses.dataclass
class ContestInfo:
    name: str
    sub_name: str
    start_time: str
    period: str
    rated: str

    def __str__(self):
        return (
            f"start time   : {self.start_time}\n"
            f"contest name : {self.name}\n"
            f"    sub name : {self.sub_name}\n"
            f"period       : {self.period}\n"
            f"rated        : {self.rated}"
        )


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

    atcoder_contests = _sorted_contests_by_relevance(name, _get_all_atcoder_marathon_contests())

    related_contest = _ask_related_contest(atcoder_contests)

    if related_contest is not None:
        logger.info(
            "this project is now associated with the following contest\n"
            "=====================================\n"
            f"{related_contest}\n"
            "=====================================\n"
        )

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))


def _get_all_atcoder_marathon_contests(overseas: bool = False) -> List[ContestInfo]:
    logger = logging.getLogger(__name__)
    logger.debug(CONST.ATCODER_PAST_MARATHON_CONTESTS_URL)

    contests = []

    detected_contest_count = 0
    recognized_contest_count = 0

    page_idx = 0
    while True:
        page_idx += 1
        url = f"{CONST.ATCODER_PAST_MARATHON_CONTESTS_URL}&lang={'en' if overseas else 'ja'}&page={page_idx}"
        content = requests.get(url)
        soup = BeautifulSoup(content.text, "html.parser")
        tables = soup.find_all("tbody")

        if not tables or page_idx >= 30:
            break

        for table in tables:
            for contest in table.find_all("tr"):
                detected_contest_count += 1
                raw_contest_info = contest.find_all("td")
                if len(raw_contest_info) == 4:
                    raw_contest_info[0] = raw_contest_info[0].find("time")
                    raw_contest_info[1] = raw_contest_info[1].find("a")

                    if all(raw_contest_info):
                        start_time, contest_name, period, rated = map(lambda x: x.text, raw_contest_info)

                        sub_contest_name = raw_contest_info[1].get("href")
                        sub_contest_name = "" if sub_contest_name is None else sub_contest_name.lstrip("/contests/")

                        recognized_contest_count += 1
                        contests.append(
                            ContestInfo(
                                name=contest_name,
                                sub_name=sub_contest_name,
                                start_time=start_time,
                                period=period,
                                rated=rated,
                            )
                        )

    logger.info(
        f"contests scraping is completed. recognized / detected: {recognized_contest_count} / {detected_contest_count}"
    )

    return contests


def _normalize_contest_name(raw_name: str) -> str:
    name = re.sub("[\W_]", "", raw_name).lower()
    name = name.replace("ahc", "atcoderheuristiccontest")
    name = name.replace("httf", "hacktothefuture")
    return name


def _calc_edit_distance(s1: str, s2: str) -> float:
    d1 = Levenshtein.distance(s1, s2) / max(len(s1), len(s2))
    d2 = 1.0 - Levenshtein.jaro_winkler(s1, s2)
    return (d1 + d2) / 2


def _sorted_contests_by_relevance(raw_name: str, atcoder_contests: List[ContestInfo]) -> List[ContestInfo]:
    name = _normalize_contest_name(raw_name)
    return list(
        map(
            lambda x: atcoder_contests[x],
            OrderedDict.fromkeys(
                map(
                    lambda x: x[1],
                    sorted(
                        [
                            (_calc_edit_distance(name, _normalize_contest_name(contest_name)), i // 2)
                            for i, contest_name in enumerate(
                                sum(map(lambda x: [x.name, x.sub_name], atcoder_contests), [])
                            )
                        ]
                    ),
                )
            ),
        )
    )


def _ask_related_contest(atcoder_contests: List[ContestInfo]) -> Optional[ContestInfo]:
    logger = logging.getLogger(__name__)
    n = len(atcoder_contests)
    ndn = len(str(n))

    print()
    skipped = False
    for_this_contest = None
    for th, contest in enumerate(atcoder_contests):
        progress = f"[{th+1:{ndn}d}/{n}] " if th != 0 else ""
        formatted_contest_name = text_styling(contest.name, color=Fore.CYAN, style=Style.BRIGHT)

        replay = input(
            f"{progress}this template will be used for {formatted_contest_name}?  [y(yes) / s(skip) / other(no)]: "
        ).strip()

        # yes: ye[s]
        if replay.endswith(("y", "yes")):
            for_this_contest = contest
            break
        elif replay.endswith(("s", "skip")):
            skipped = True
            break

        # todo: adjust to terminal size
        print("\033[1A\033[2K", end="")
        sys.stdout.flush()

    if not skipped and for_this_contest is None:
        logger.info("No further contest information available...")
    print()

    return for_this_contest
