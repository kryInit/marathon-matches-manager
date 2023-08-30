import sys
from typing import Optional

from colorama import Fore, Style
from logzero import logger

from ..contests import fetch_all_atcoder_heuristic_contests, sorted_contests_by_relevance
from ..misc import text_styling
from ..models import Contest


def ask_related_contest(name: str, overseas: bool = False) -> Optional[Contest]:
    atcoder_contests = sorted_contests_by_relevance(name, fetch_all_atcoder_heuristic_contests(overseas))
    contest_count = len(atcoder_contests)
    contest_count_digit_len = len(str(contest_count))

    print()
    skipped = False
    target_contest = None
    for th, contest in enumerate(atcoder_contests):
        progress = f"[{th+1:{contest_count_digit_len}d}/{contest_count}] " if th != 0 else ""
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
        # revert output
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
