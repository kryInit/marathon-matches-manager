from __future__ import annotations

import os
from typing import Dict, Optional

import toml
from logzero import logger
from pydantic import BaseModel, Field, root_validator

from ..misc.const import CONST
from ..utils import expand_env_variables
from .command import Command, GenCaseCommand, TestConfig
from .contest import Contest

# base config的なものを作ったほうがいいと思うんだよな
# global configでproject configを埋める感じで


class BaseConfig(BaseModel):
    environment: Dict[str, str] = {}
    initialize: Optional[Command]
    commands: Dict[str, Command] = {}
    test: Optional[TestConfig]
    solver: Dict[str, Command] = {}
    judge: Dict[str, Command] = {}
    evaluator: Dict[str, Command] = {}
    gen_case: Dict[str, GenCaseCommand] = Field(default={}, alias="gen-case")

    # todo: 流石にroot_validatorでos.environという実質global変数に代入するのは良くない気がするのだが、あまり良い方法を思いつかない
    @root_validator(pre=True)
    def set_env_vars(cls, values: dict) -> dict:
        if not isinstance(values, dict) or "environment" not in values or not isinstance(values["environment"], dict):
            return values

        for key, value in values["environment"].items():
            os.environ[key] = str(value)
        for key, _ in values["environment"].items():
            os.environ[key] = expand_env_variables(os.environ[key])

        return values

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

    # todo: こっちも流石にroot_validatorでos.environという実質global変数に代入するのは良くない気がするのだが、あまり良い方法を思いつかない
    @root_validator(pre=True)
    def set_env_vars(cls, values: dict) -> dict:
        if not isinstance(values, dict) or "contest" not in values or not isinstance(values["contest"], dict):
            return values
        contest = values["contest"]
        if "environment" not in contest or not isinstance(contest["environment"], dict):
            return values

        for key, value in contest["environment"].items():
            os.environ[key] = str(value)
        for key, _ in contest["environment"].items():
            os.environ[key] = expand_env_variables(os.environ[key])

        return values

    def update_os_environment(self):
        for key, value in self.environment.items():
            os.environ[key] = value

        if self.contest is not None:
            for key, value in self.contest.environment.items():
                os.environ[key] = value

        for key, value in self.environment.items():
            os.environ[key] = expand_env_variables(value)

        if self.contest is not None:
            for key, value in self.contest.environment.items():
                os.environ[key] = expand_env_variables(value)
