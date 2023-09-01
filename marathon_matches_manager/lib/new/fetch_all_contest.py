import re
from collections import namedtuple
from typing import List

import Levenshtein
import requests
from bs4 import BeautifulSoup
from logzero import logger

from ..misc.const import CONST
from ..models import Contest


def fetch_all_atcoder_heuristic_contests_sorted_by_relevance(name: str, overseas: bool) -> List[Contest]:
    return sorted_contests_by_relevance(name, fetch_all_atcoder_heuristic_contests(overseas))


def fetch_all_atcoder_heuristic_contests(overseas: bool) -> List[Contest]:
    logger.debug(CONST.ATCODER_PAST_HEURISTIC_CONTESTS_URL)

    page_num_limit = 30

    contests = []
    detected_contest_count = 0
    recognized_contest_count = 0

    """
    model: 
    <tbody>
        <tr>
            <td> <time> {time} </time> </td>
            <td> <a href=/contests/{sub constest name}> {contest name} </a> </td>
            <td> {time_limit} </td>
            <td> {is_rated} </td>
        </tr>
        ...
    </tbody>
    """
    for page_idx in range(1, page_num_limit):
        url = f"{CONST.ATCODER_PAST_HEURISTIC_CONTESTS_URL}&lang={'en' if overseas else 'ja'}&page={page_idx}"
        content = requests.get(url)
        soup = BeautifulSoup(content.text, "html.parser")
        tables = soup.find_all("tbody")

        if not tables:
            break

        for table in tables:
            for contest in table.find_all("tr"):
                detected_contest_count += 1
                raw_contest_info = contest.find_all("td")

                # tdの数が4(想定)でなければスキップ
                if len(raw_contest_info) != 4:
                    continue

                # <time>タグと<a>タグを取得
                raw_contest_info[0] = raw_contest_info[0].find("time")
                raw_contest_info[1] = raw_contest_info[1].find("a")

                # contest infoの要素いずれかがNoneであればスキップ
                if not all(raw_contest_info):
                    continue

                start_time, contest_name, time_limit, is_rated = map(lambda x: x.text, raw_contest_info)

                contest_rel_url = raw_contest_info[1].get("href")
                url = CONST.ATCODER_URL + contest_rel_url
                sub_contest_name = "" if contest_rel_url is None else contest_rel_url.lstrip("/contests/")

                recognized_contest_count += 1
                contests.append(
                    Contest(
                        url=url,
                        name=contest_name,
                        sub_name=sub_contest_name,
                        start_time=start_time,
                        time_limit=time_limit,
                        is_rated=is_rated,
                    )
                )

    logger.info(
        f"contests scraping is completed. recognized / detected: {recognized_contest_count} / {detected_contest_count}"
    )

    return contests


def sorted_contests_by_relevance(requested_contest_name: str, atcoder_contests: List[Contest]) -> List[Contest]:
    normed_requested_contest_name = normalize_contest_name(requested_contest_name)

    WeightedContest = namedtuple("WeightedContest", ["priority", "contest"])

    weighted_contests = [
        WeightedContest(
            priority=max(
                calc_str_relevance(normed_requested_contest_name, normalize_contest_name(contest.name)),
                calc_str_relevance(normed_requested_contest_name, normalize_contest_name(contest.sub_name)),
            ),
            contest=contest,
        )
        for contest in atcoder_contests
    ]

    return list(map(lambda x: x.contest, sorted(weighted_contests, key=lambda x: x.priority)))


def normalize_contest_name(raw_name: str) -> str:
    # delete whitespace and underscore, and to lower
    name = re.sub("[\W_]", "", raw_name).lower()

    # normalize
    name = name.replace("ahc", "atcoder heuristic contest".replace(" ", ""))
    name = name.replace("httf", "hack to the future".replace(" ", ""))

    return name


def calc_str_relevance(s1: str, s2: str) -> float:
    # using edit distance
    d1 = Levenshtein.distance(s1, s2) / max(len(s1), len(s2))
    d2 = 1.0 - Levenshtein.jaro_winkler(s1, s2)
    return (d1 + d2) / 2
