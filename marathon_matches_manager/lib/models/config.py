from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import toml
from pydantic import BaseModel, Field, root_validator

from ..misc.const import CONST
from ..utils import expand_env_variables
from .command import Command, GenCaseCommand, TestConfig
from .contest import Contest

# base config的なものを作ったほうがいいと思うんだよな
# global configでproject configを埋める感じで


class BaseConfig(BaseModel):
    initialize: Optional[Command]
    environment: Dict[str, str] = {}
    commands: Dict[str, Command] = {}
    tester: Optional[TestConfig]
    solver: Dict[str, Command] = {}
    judge: Dict[str, Command] = {}
    evaluator: Dict[str, Command] = {}
    gen_case: Dict[str, GenCaseCommand] = Field(default={}, alias="gen-case")

    @root_validator(pre=True)
    def set_command_name(cls, values: dict) -> dict:
        # コマンドに対する命名
        # todo: なんか雑な気がするのであとで確認

        if "initialize" in values:
            if "name" not in values["initialize"]:
                values["initialize"]["name"] = "initialize"

        properties = ["commands", "solver", "judge", "evaluator", "gen-case"]
        for prop in properties:
            if prop not in values:
                continue
            for key, value in values[prop].items():
                if "name" not in values[prop][key]:
                    prefix = "" if prop == "commands" else f"{prop}."
                    values[prop][key]["name"] = prefix + key

        return values

    def update_os_environment(self):
        for key, value in self.environment.items():
            os.environ[key] = value
        for key, value in self.environment.items():
            os.environ[key] = expand_env_variables(value)

    @classmethod
    def get_global_config(cls) -> BaseConfig:
        return cls.parse_obj(toml.load(open(CONST.GLOBAL_CONFIG_FILE_PATH)))


class ProjectConfig(BaseConfig):
    project_name: str
    contest: Optional[Contest]

    # class Config:
    #     exclude = {"initialize"}

    def update_os_environment(self):
        for key, value in self.environment.items():
            os.environ[key] = value
        for key, value in self.contest.environment.items():
            os.environ[key] = value
        for key, value in self.environment.items():
            os.environ[key] = expand_env_variables(value)
        for key, value in self.contest.environment.items():
            os.environ[key] = expand_env_variables(value)
