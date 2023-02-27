import logging
from typing import List

import requests
from bs4 import BeautifulSoup

from ..const import CONST
from ..models import Contest


def fetch_all_atcoder_heuristic_contests(overseas: bool) -> List[Contest]:
    logger = logging.getLogger(__name__)
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
                if len(raw_contest_info) == 4:
                    raw_contest_info[0] = raw_contest_info[0].find("time")
                    raw_contest_info[1] = raw_contest_info[1].find("a")

                    if all(raw_contest_info):
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
