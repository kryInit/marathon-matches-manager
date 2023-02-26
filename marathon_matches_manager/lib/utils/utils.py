import Levenshtein


def calc_str_relevance(s1: str, s2: str) -> float:
    # using edit distance
    d1 = Levenshtein.distance(s1, s2) / max(len(s1), len(s2))
    d2 = 1.0 - Levenshtein.jaro_winkler(s1, s2)
    return (d1 + d2) / 2
