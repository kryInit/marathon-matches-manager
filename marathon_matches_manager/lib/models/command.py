import hashlib
import os
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from logzero import logger
from pydantic import BaseModel, Field, root_validator, validator

from ..utils import expand_env_variables


class Command(BaseModel):
    name: str
    run: List[str] = []
    working_directory: Path = Field(default=Path("${project_root_path}"), alias="working-directory")
    disable: bool = False
    timeout: timedelta = timedelta(seconds=300)

    @validator("run", pre=True)
    def convert_single_run_cmd_to_list(cls, run: Any):
        if isinstance(run, str):
            return [run]
        return run

    def exec(
        self, env=os.environ, stdout=None, stderr=None, dump_log: bool = False
    ) -> List[subprocess.CompletedProcess]:
        if dump_log:
            logger.info(f"exec command: {self.name}")
        ret = []
        for cmd in self.run:
            # todo: multi-lineに対処, doneとかexecuting...とかやりたいね
            if dump_log:
                logger.info(f"    -> exec sub command: {cmd}")

            # todo: disableいる？, 出力情報どうする？, os.environ経由する必要ある？
            result = subprocess.run(
                cmd,
                env=env,
                shell=True,
                cwd=expand_env_variables(self.working_directory),
                timeout=self.timeout.seconds,
                stdout=stdout,
                stderr=stderr,
            )
            ret.append(result)
        return ret


class TestCase(BaseModel):
    file_name: str


class TestSuite(BaseModel):
    name: str
    case_files: List[str]
    hash: str

    def get_cases(self) -> List[TestCase]:
        return [TestCase(file_name=file_name) for file_name in self.case_files]


class GenCaseCommand(Command):
    case_paths: List[Path] = Field(alias="case-paths")
    clean: bool = True

    @validator("case_paths", pre=True)
    def ensure_list(cls, case_paths: Any) -> Any:
        return [case_paths] if isinstance(case_paths, str) or isinstance(case_paths, Path) else case_paths

    @validator("case_paths")
    def ensure_non_empty(cls, values: List[str]) -> List[str]:
        if not values:
            raise ValueError("gen-case.case_paths should have at least one path")
        return values


class TestCaseConfig(BaseModel):
    path: Path = Path("${project_root_path}/cases")
    generator: Dict[str, GenCaseCommand]

    @root_validator(pre=True)
    def set_command_name(cls, values: dict) -> dict:
        # todo: コマンドに対する命名よくやるので抽象化したくね？
        if "generator" in values and isinstance(values["generator"], dict):
            for key, value in values["generator"].items():
                if "name" not in value:
                    values["generator"][key]["name"] = key

        return values

    @validator("path")
    def expand_env_var(cls, path: Path) -> Path:
        return expand_env_variables(path)


class TestSuiteConfig(BaseModel):
    path: Path = Path("${project_root_path}/suites")

    @validator("path")
    def expand_env_var(cls, path: Path) -> Path:
        return expand_env_variables(path)


class TestLogConfig(BaseModel):
    path: Path = Path("${project_root_path}/logs")

    @validator("path")
    def expand_env_var(cls, path: Path) -> Path:
        return expand_env_variables(path)


class TestConfig(BaseModel):
    default_concurrency: int = 1
    case: TestCaseConfig
    suite: TestSuiteConfig
    log: TestLogConfig


# class TestCaseManager:
#     @classmethod
#     def save(cls, case_path: Path) -> TestCase:
#         environment.global_config
