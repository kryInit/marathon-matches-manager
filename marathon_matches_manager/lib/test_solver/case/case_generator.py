import hashlib
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterable, List

import toml
from logzero import logger
from pydantic import BaseModel

from ...misc import environment
from ...models.command import GenCaseCommand, TestCase, TestSuite
from ...utils import expand_env_variables, remove_any_file


def flatten_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from flatten_files(path.iterdir())


class TestCaseGenerator:
    @classmethod
    def generate(cls, command: GenCaseCommand) -> List[TestCase]:
        dest_base_path = Path(expand_env_variables(environment.global_config.tester.case.path))
        paths = flatten_files(command.case_paths)

        if not dest_base_path.exists():
            logger.info(f"create case directory: {dest_base_path}")
            dest_base_path.mkdir(parents=True)

        command.exec()
        try:
            ret = cls.move_cases(paths, dest_base_path)
        except Exception as e:
            logger.error(f"failed to move cases. cleaning up...")
            raise e
        finally:
            if command.clean:
                cls._cleanup(command.case_paths)

        return ret

    @classmethod
    def move_cases(cls, source_paths: Iterable[Path], dest_base_path: Path):
        ret = []
        for case_path in source_paths:
            if not case_path.exists():
                logger.warning(
                    f"case path not found: {case_path}, may have been deleted after searching the directory"
                )
                continue

            hash_value = hashlib.sha256(open(case_path, "rb").read()).hexdigest()
            file_name = f"{hash_value}.txt"
            dest_case_path = dest_base_path.joinpath(file_name)
            if dest_case_path.exists():
                continue
            shutil.copy(expand_env_variables(str(case_path)), expand_env_variables(str(dest_case_path)))
            ret.append(TestCase(file_name=file_name))
        return ret

    @classmethod
    def _cleanup(cls, generated_case_paths: List[Path]) -> None:
        for path in generated_case_paths:
            remove_any_file(path)


class TestSuiteGenerator:
    @classmethod
    def generate(cls, suite_name: str, command: GenCaseCommand) -> TestSuite:
        cases = TestCaseGenerator.generate(command)
        suite_path = environment.global_config.tester.suite.path.joinpath(f"{suite_name}")
        if suite_path.exists():
            logger.error(f"test suite path already exists: {suite_path}")
            raise FileExistsError

        case_files = list(sorted(map(lambda x: x.file_name, cases)))
        hash_str = hashlib.sha256("/".join(case_files).encode()).hexdigest()
        suite = TestSuite(name=suite_name, case_files=case_files, hash=hash_str)

        Path(expand_env_variables(str(suite_path))).mkdir(parents=True)
        with open(expand_env_variables(str(suite_path.joinpath("config.toml"))), "w") as f:
            toml.dump(suite.dict(), f)

        return suite


# class ITestCaseGenerator(ABC):
#     @abstractmethod
#     def postprocess(self, generated_case_paths: List[Path]) -> None:
#
#     @abstractmethod
#     def generate(self, command: GenCaseCommand) -> List[Path]:
#         raise NotImplementedError
#
#
# class ITestSuiteGenerator(ABC):
#     @abstractmethod
#     def postprocess(self, generated_suite_path: Path) -> None:
#         raise NotImplementedError
#
#     @abstractmethod
#     def generate(self) -> Path:
#         raise NotImplementedError
#
#
# # case作るときに色々やりたくなったりしないかなというやつ
#
# class DefaultTestCaseGenerator(ITestCaseGenerator):
#     def __init__(self):
#         pass
#
#     def postprocess(self, generated_case_paths: List[Path]) -> None:
#         super().postprocess(generated_case_paths)
#
#     def generate(self, command: GenCaseCommand) -> List[Path]:
#         pass
#
# class ConfiguredTestSuiteGenerator(ITestSuiteGenerator):
#     def __init__(self):
#         pass
#
#     def postprocess(self, generated_suite_path: Path) -> None:
#         super().postprocess(generated_suite_path)
#
#     def generate(self) -> Path:
#         pass
