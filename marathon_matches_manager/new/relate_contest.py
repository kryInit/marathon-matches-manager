import logging
import re
import sys
from collections import OrderedDict
from typing import List, Optional

import Levenshtein
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style

from marathon_matches_manager.const import CONST
from marathon_matches_manager.new.models.contest import Contest
from marathon_matches_manager.utils.text_styling import text_styling


def ask_related_contest(name: str, overseas: bool = False) -> Optional[Contest]:
    atcoder_contests = _sorted_contests_by_relevance(name, _get_all_atcoder_marathon_contests(overseas))
    logger = logging.getLogger(__name__)
    n = len(atcoder_contests)
    ndn = len(str(n))

    print()
    skipped = False
    target_contest = None
    for th, contest in enumerate(atcoder_contests):
        progress = f"[{th+1:{ndn}d}/{n}] " if th != 0 else ""
        formatted_contest_name = text_styling(contest.name, color=Fore.CYAN, style=Style.BRIGHT)

        replay = input(
            f"{progress}this template will be used for {formatted_contest_name}?  [y(yes) / s(skip) / other(no)]: "
        ).strip()

        # suffix of "yes" is s, which is prefix of "skip"
        if replay.endswith(("y", "yes")):
            target_contest = contest
            break
        elif replay.endswith(("s", "skip")):
            skipped = True
            break

        # todo: adjust to terminal size
        print("\033[1A\033[2K", end="")
        sys.stdout.flush()

    if not skipped and target_contest is None:
        logger.info("No further contest information available...")
    print()

    if target_contest:
        logger.info(
            "this project has been related to the following contest\n"
            "=====================================\n"
            f"{target_contest}\n"
            "=====================================\n"
        )

    return target_contest


def _get_all_atcoder_marathon_contests(overseas: bool) -> List[Contest]:
    logger = logging.getLogger(__name__)
    logger.debug(CONST.ATCODER_PAST_MARATHON_CONTESTS_URL)

    contests = []

    detected_contest_count = 0
    recognized_contest_count = 0

    page_num_limit = 30
    for page_idx in range(1, page_num_limit):
        url = f"{CONST.ATCODER_PAST_MARATHON_CONTESTS_URL}&lang={'en' if overseas else 'ja'}&page={page_idx}"
        content = requests.get(url)
        soup = BeautifulSoup(content.text, "html.parser")
        tables = soup.find_all("tbody")

        if not tables:
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
                            Contest(
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


def _sorted_contests_by_relevance(raw_name: str, atcoder_contests: List[Contest]) -> List[Contest]:
    name = _normalize_name(raw_name)
    return list(
        map(
            lambda i: atcoder_contests[i],
            OrderedDict.fromkeys(
                map(
                    lambda x: x[1],
                    sorted(
                        [
                            (_calc_relevance(name, _normalize_name(contest_name)), i // 2)
                            for i, contest_name in enumerate(
                                sum(map(lambda x: [x.name, x.sub_name], atcoder_contests), [])
                            )
                        ]
                    ),
                )
            ),
        )
    )


def _normalize_name(raw_name: str) -> str:
    name = re.sub("[\W_]", "", raw_name).lower()
    name = name.replace("ahc", "atcoderheuristiccontest")
    name = name.replace("httf", "hacktothefuture")
    return name


def _calc_relevance(s1: str, s2: str) -> float:
    # using edit distance
    d1 = Levenshtein.distance(s1, s2) / max(len(s1), len(s2))
    d2 = 1.0 - Levenshtein.jaro_winkler(s1, s2)
    return (d1 + d2) / 2
