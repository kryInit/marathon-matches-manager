import dataclasses
from typing import List, Union


@dataclasses.dataclass
class OfficialTools:
    tools_url: str
    visualizer_url: str
    tools_path: str
    targets: Union[str, List[str]]

    def __init__(self, official_tools_dict: dict):
        pass
