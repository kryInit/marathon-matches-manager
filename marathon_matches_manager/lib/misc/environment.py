from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import toml
from logzero import logger
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from ..models import BaseConfig, ProjectConfig
from .const import CONST


@dataclass(frozen=True)
class Environment(BaseModel):
    in_project: bool
    project_root_path: Optional[Path]
    project_config_path: Optional[Path]
    project_config: Optional[ProjectConfig]
    global_config: BaseConfig

    def show(self) -> str:
        return json.dumps(json.loads(self.json(exclude_unset=True)), indent=2)

    @classmethod
    def create(cls) -> Environment:
        # todo: ちゃんとパースする、なければデフォルト値で埋める
        global_config: BaseConfig = BaseConfig.get_global_config()
        global_config.update_os_environment()

        current_path = Path.cwd()

        # until reach root
        while current_path.parent != current_path:
            # founded config file
            if current_path.joinpath(CONST.CONFIG_FILE_NAME).exists():
                config_file_path = current_path.joinpath(CONST.CONFIG_FILE_NAME)
                project_config: ProjectConfig = ProjectConfig.parse_obj(toml.load(open(config_file_path)))

                # todo: ここめっちゃ汚いよな・・・
                os.environ["project_root_path"] = str(current_path)
                global_config.update_os_environment()
                project_config.update_os_environment()

                env = Environment(
                    in_project=True,
                    project_root_path=current_path,
                    project_config_path=current_path.joinpath(CONST.CONFIG_FILE_NAME),
                    project_config=project_config,
                    global_config=global_config,
                )

                return env

            current_path = current_path.parent

        # not founded config file
        return Environment(
            in_project=False,
            project_root_path=None,
            project_config_path=None,
            project_config=None,
            global_config=global_config,
        )


environment = Environment.create()
