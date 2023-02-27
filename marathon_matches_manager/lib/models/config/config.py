import dataclasses
from pathlib import Path
from typing import Optional, Type, TypeAlias

import toml

from ..contest import Contest
from .official_tools import OfficialTools
from .project import Project


@dataclasses.dataclass
class Config:
    project: Project
    contest: Optional[Contest]
    official_tools: Optional[OfficialTools]

    def __init__(self, config_path: Path):
        config_dict = toml.load(config_path)

        # if 'project' not in config_dict:
        # self.project = Project()
        # else:
        #     self.project = Project(config_dict['project'])

        if "contest" not in config_dict:
            self.contest = None
        # else:
        #     self.contest = Contest(config_dict['contest'])

        if "official-tools" not in config_dict:
            self.official_tools = None
        else:
            self.official_tools = OfficialTools(config_dict["official-tools"])
