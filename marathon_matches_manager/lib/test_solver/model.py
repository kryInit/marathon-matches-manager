from typing import List

from marathon_matches_manager.lib.models.command import TestCase


class TestResult:
    case: TestCase
    result: List[str]

    def __init__(self, case: TestCase, result: List[str]):
        self.case = case
        self.result = result
