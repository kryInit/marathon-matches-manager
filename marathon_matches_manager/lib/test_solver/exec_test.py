import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Tuple, Union

import toml
from logzero import logger
from tqdm import tqdm

from ..misc import environment
from ..models import Command
from ..utils import expand_env_variables, remove_any_file
from .case import TestCase, TestSuite


class Solver:
    cmd: Command

    def __init__(self, cmd: Command):
        self.cmd = cmd


class Judge:
    cmd: Command

    def __init__(self, cmd: Command):
        self.cmd = cmd


class Evaluator:
    cmd: Command

    def __init__(self, cmd: Command):
        self.cmd = cmd

    def evaluate(self, env: Dict[str, str]) -> str:
        with NamedTemporaryFile("r") as f:
            env["evaluator_output"] = f.name
            self.cmd.exec(env=env)
            return f.read()


class IOFIleNames:
    input_file: str
    answer: str
    solver_output: str
    judge_output: str

    def __init__(self, input_file_path: Union[str, Path]):
        input_file_path = str(input_file_path)
        self.input_file = input_file_path
        self.answer = input_file_path + ".answer"
        self.solver_output = input_file_path + ".solver_output"
        self.judge_output = input_file_path + ".judge_output"

    def make_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env["input_file"] = self.input_file
        env["answer"] = self.answer
        env["solver_output"] = self.solver_output
        env["judge_output"] = self.judge_output
        return env


class TestResult:
    case: TestCase
    result: List[str]

    def __init__(self, case: TestCase, result: List[str]):
        self.case = case
        self.result = result


class TestRunner:
    solver: Solver
    judge: Judge
    evaluators: List[Evaluator]

    def __init__(self, solver: Solver, judge: Judge, evaluators: List[Evaluator]):
        self.solver = solver
        self.judge = judge
        self.evaluators = evaluators

    @classmethod
    def run_on_suite(
        cls,
        suite_name: str,
        solver_name: str = "main",
        judge_name: str = "main",
        evaluator_names: List[str] = None,
        concurrency: Optional[int] = None,
    ) -> List[TestResult]:
        if evaluator_names is None:
            evaluator_names = ["main"]
        if concurrency is None:
            concurrency = environment.project_config.test.default_concurrency

        environment.project_config.test.pre_cmd.exec()

        solver = Solver(cmd=environment.project_config.solver[solver_name])
        judge = Judge(cmd=environment.project_config.judge[judge_name])
        evaluators = [Evaluator(cmd=environment.project_config.evaluator[name]) for name in evaluator_names]

        suite_path = expand_env_variables(environment.project_config.test.suite.path).joinpath(suite_name)
        if not suite_path.exists():
            raise Exception(f"test suite not found: {suite_path}")
        suite = TestSuite.parse_obj(toml.load(suite_path.joinpath("config.toml")))

        result = cls(solver, judge, evaluators).run_on_suite_helper(suite, concurrency)

        scores = list(map(lambda x: int(x.result[0]), result))
        score_sum = sum(scores)
        score_ave = score_sum / len(scores)
        result_with_max_score = max(result, key=lambda x: int(x.result[0]))
        result_with_min_score = min(result, key=lambda x: int(x.result[0]))

        logger.info(f"[test result | score] sum: {score_sum}, ave: {score_ave}")
        logger.info(
            f"                      max: {int(result_with_max_score.result[0])}, name: {result_with_max_score.case.file_name[:5]}..."
        )
        logger.info(
            f"                      min: {int(result_with_min_score.result[0])}, name: {result_with_min_score.case.file_name[:5]}..."
        )

        return result

    @classmethod
    def run_on_case(
        cls,
        case_path: str,
        solver_name: str = "main",
        judge_name: str = "main",
        evaluator_names: List[str] = None,
    ) -> TestResult:
        if evaluator_names is None:
            evaluator_names = ["main"]

        environment.project_config.test.pre_cmd.exec()

        solver = Solver(cmd=environment.project_config.solver[solver_name])
        judge = Judge(cmd=environment.project_config.judge[judge_name])
        evaluators = [Evaluator(cmd=environment.project_config.evaluator[name]) for name in evaluator_names]

        case_path = Path(case_path)
        if not case_path.exists():
            raise Exception(f"test case not found: {case_path}")
        case = TestCase(file_name=case_path.name)

        result = cls(solver, judge, evaluators).run_on_case_helper(case)

        logger.info(f"[test result | score] {int(result.result[0])}")

        return result

    def run_on_suite_helper(self, suite: TestSuite, concurrency: int) -> List[TestResult]:
        cases = suite.get_cases()
        ret = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            results = executor.map(self.run_on_case_helper, cases)
            for result in tqdm(results, total=len(cases), miniters=concurrency):
                ret.append(result)
        return ret

    def run_on_case_helper(self, case: TestCase) -> TestResult:
        case_path = expand_env_variables(environment.project_config.test.case.path).joinpath(case.file_name)
        file_names = IOFIleNames(case_path)
        env = file_names.make_env()

        # solver.cmdは内部で${input_file}と${answer}, ${solver_output}を使う
        self.solver.cmd.exec(env=env)

        # judge.cmdは内部で${input_file}と${answer}, ${solver_output}と${judge_output}を使う
        self.judge.cmd.exec(env=env)

        # evaluator.cmdは内部で${input_file}と${answer}${solver_output}と${judge_output}と${evaluator_output}を使う
        result = [evaluator.evaluate(env=env) for evaluator in self.evaluators]

        # todo:　ログは適当な場所に置いておいたほうが良い気はする
        temporary_files = [file_names.answer, file_names.solver_output, file_names.judge_output]
        for file_name in temporary_files:
            if os.path.exists(file_name):
                os.remove(file_name)

        return TestResult(case=case, result=result)


"""
class TestExecutor:
    @classmethod
    def exec_by_name(cls, name: str):
        suites_dir = Path(expand_env_variables(environment.project_config.tester.suite.path))
        suite_path = suites_dir.joinpath(name)
        if not suite_path.exists():
            raise Exception(f"test suite not found: {suite_path}")
        suite = TestSuite.parse_obj(toml.load(suite_path.joinpath("config.toml")))
        cls.exec(suite)

    @classmethod
    def exec(cls, suite: TestSuite):
        output_base_path = Path(
            expand_env_variables(environment.project_config.tester.log.path.joinpath("prev_outputs"))
        )

        if output_base_path.exists():
            remove_any_file(output_base_path)
        output_base_path.mkdir(parents=True)

        input_base_path = Path(expand_env_variables(environment.project_config.tester.case.path))
        input_paths = [input_base_path.joinpath(file_name) for file_name in suite.case_files]
        output_paths = [output_base_path.joinpath(file_name) for file_name in suite.case_files]

        scores = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(cls._exec_helper, input_paths, output_paths)
            for result in results:
                scores.append(result)
        print(sum(scores))

    @classmethod
    def _exec_helper(cls, input_path: Path, output_path: Path) -> int:
        env = os.environ.copy()
        env["input_file"] = str(input_path.absolute())
        env["output_file"] = str(output_path.absolute())
        solver = environment.project_config.solver["main"]
        solver.exec(env=env)
        scoring = environment.project_config.scoring["main"]

        scoring_output_text = scoring.exec(env=env, stdout=subprocess.PIPE)[-1].stdout
        return int(scoring_output_text.split()[-1])


# todo: tuple綺麗じゃない
def exec_test_helper(io_path: Tuple[Path, Path]):
    input_file_path = io_path[0]
    output_file_path = io_path[1]
    env = os.environ.copy()
    env["input_file"] = str(input_file_path.absolute())
    env["output_file"] = str(output_file_path.absolute())

    command = environment.project_config.scoring["main"]
    for cmd in command.run_on_case:
        result = subprocess.run(
            cmd,
            env=env,
            shell=True,
            cwd=os.path.expandvars(command.working_directory),
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE
        )
    # print(result.stdout)
    return int(result.stdout.split()[-1])


def exec_test(inputs_path: str, outputs_path: str):
    inputs_path = expand_env_variables(inputs_path)
    outputs_path = expand_env_variables(outputs_path)

    input_file_paths = list(
        map(
            lambda x: (Path(x), Path(outputs_path).joinpath(Path(x).name)),
            glob.glob(str(Path(inputs_path).joinpath("*"))),
        )
    )

    scores = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(exec_test_helper, input_file_paths)
        for result in results:
            scores.append(result)
    print(sum(scores))

"""
