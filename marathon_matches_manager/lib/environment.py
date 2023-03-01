from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import toml
from pydantic import BaseModel

from .const import CONST
from .models import ProjectConfig


class Environment(BaseModel):
    in_project: bool
    project_root_path: Optional[Path]
    project_config_path: Optional[Path]
    project_config: Optional[ProjectConfig]

    @classmethod
    def create(cls) -> Environment:
        current_path = Path.cwd()

        # until reach root
        while current_path.parent != current_path:
            # founded config file
            if current_path.joinpath(CONST.CONFIG_FILE_NAME).exists():
                return Environment(
                    in_project=True,
                    project_root_path=current_path,
                    project_config_path=current_path.joinpath(CONST.CONFIG_FILE_NAME),
                    project_config=ProjectConfig.parse_obj(
                        toml.load(open(current_path.joinpath(CONST.CONFIG_FILE_NAME)))
                    ),
                )
            current_path = current_path.parent

        # not founded config file
        return Environment(in_project=False, project_root_path=None, project_config_path=None, project_config=None)


environment = Environment.create()
