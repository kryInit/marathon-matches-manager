import dataclasses
from typing import List, Union


@dataclasses.dataclass
class Command:
    name: str
    run: Union[str, List[str]]
    working_directory: str
    disable: bool
    timeout: Union[str, int]

    def __init__(self, command_dict: dict):
        pass
