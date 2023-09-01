
from ..models import Contest
from urllib.parse import urljoin


def fetch_detailed_contest(contest: Contest) -> Contest:
    return contest