import re
from collections import OrderedDict
from typing import List

from ..misc import calc_str_relevance
from ..models import Contest


def sorted_contests_by_relevance(requested_contest_name: str, atcoder_contests: List[Contest]) -> List[Contest]:
    normed_requested_contest_name = _normalize_name(requested_contest_name)

    # sum( [[str]], [] ) -> [str]: flatten
    candidates: List[str] = sum(map(lambda x: [x.name, x.sub_name], atcoder_contests), [])

    # i // 2: a contest has two names: name and sub name
    candidates_with_priority = [
        (calc_str_relevance(normed_requested_contest_name, _normalize_name(contest_name)), i // 2)
        for i, contest_name in enumerate(candidates)
    ]

    sorted_candidates_indices = map(lambda x: x[1], sorted(candidates_with_priority))

    distinct_sorted_candidates_indices = OrderedDict.fromkeys(sorted_candidates_indices)

    distinct_sorted_candidates = list(map(lambda i: atcoder_contests[i], distinct_sorted_candidates_indices))

    return distinct_sorted_candidates


def _normalize_name(raw_name: str) -> str:
    # delete whitespace and underscore, and to lower
    name = re.sub("[\W_]", "", raw_name).lower()

    # normalize
    name = name.replace("ahc", "atcoder heuristic contest".replace(" ", ""))
    name = name.replace("httf", "hack to the future".replace(" ", ""))

    return name
