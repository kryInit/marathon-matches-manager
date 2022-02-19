import dataclasses
import logging
import os
import re
from collections import OrderedDict
from typing import List

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

    atcoder_contests = _get_all_atcoder_marathon_contests()
    predicted_contests = _predict_related_contests(name, atcoder_contests)

    print()
    for contest in predicted_contests:
        formatted_contest_name = text_styling(contest.name, color=Fore.CYAN, style=Style.BRIGHT)
        replay = input(f"this template will be used for {formatted_contest_name}?  [y/n/s(skip)]: ").strip()
        if replay == "s" or replay == "skip":
            break
        elif replay == "y" or replay == "yes":
            for_this_contest = contest
            break
    print()

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))


def _get_all_atcoder_marathon_contests(overseas: bool = False) -> List[ContestInfo]:
    logger = logging.getLogger(__name__)
    logger.debug(CONST.ATCODER_PAST_MARATHON_CONTESTS_URL)

    contests = []

    url = CONST.ATCODER_PAST_MARATHON_CONTESTS_URL + "&lang=" + ("en" if overseas else "ja")
    content = requests.get(url)
    soup = BeautifulSoup(content.text, "html.parser")
    tables = soup.find_all("tbody")

    detected_contest_count = 0
    recognized_contest_count = 0

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

    logger.debug(f"scraping contests. recognized / detected: {recognized_contest_count} / {detected_contest_count}")

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


def _predict_related_contests(raw_contest_name: str, atcoder_contests: List[ContestInfo]) -> List[ContestInfo]:
    # name, url, period, in progress,

    contest_name = _normalize_contest_name(raw_contest_name)

    edit_dists = list(
        map(
            lambda x: atcoder_contests[x[1]],
            OrderedDict.fromkeys(
                sorted(
                    [
                        (_calc_edit_distance(contest_name, _normalize_contest_name(contest.name)), i)
                        for i, contest in enumerate(atcoder_contests)
                    ]
                    + [
                        (_calc_edit_distance(contest_name, _normalize_contest_name(contest.sub_name)), i)
                        for i, contest in enumerate(atcoder_contests)
                        if contest.sub_name
                    ],
                ),
            ),
        )
    )

    return edit_dists
