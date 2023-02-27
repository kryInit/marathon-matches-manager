import os
import subprocess
from invoke import task
from pathlib import Path

from colorama import Fore, Style

project_root_path = Path(__file__).parent.resolve()
source_root_path = project_root_path.joinpath('marathon_matches_manager')


@task
def lint(c):
    os.chdir(project_root_path)

    lint_commands = [
        f"mypy {source_root_path}",
        f"isort --check-only {source_root_path}",
        f"black --check {source_root_path}"
    ]

    for cmd in lint_commands:
        exec_command(cmd)


@task
def format(c):
    os.chdir(project_root_path)

    format_commands = [
        f"isort {source_root_path}",
        f"black {source_root_path}"
    ]

    for cmd in format_commands:
        exec_command(cmd)


@task
def lf(c):
    os.chdir(project_root_path)

    lint_and_format_commands = [
        f"mypy {source_root_path}",
        f"isort {source_root_path}",
        f"black {source_root_path}"
    ]

    for cmd in lint_and_format_commands:
        exec_command(cmd)


def exec_command(cmd: str):
    result = subprocess.run(cmd.split())

    cmd_name = cmd.split()[0]
    if result.returncode == 0:
        print(f"[{cmd_name}] {Fore.GREEN}{Style.BRIGHT}Passed{Style.RESET_ALL}\n")
    else:
        print(f"[{cmd_name}] {Fore.RED}{Style.BRIGHT}Failed{Style.RESET_ALL}\n")
