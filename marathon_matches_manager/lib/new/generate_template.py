import sys
from ..models import Contest

import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import toml
from colorama import Fore, Style
from logzero import logger
from typing import Optional

from ..misc import CONST, environment, text_styling
from ..models import ProjectConfig
from .fetch_all_contest import fetch_all_atcoder_heuristic_contests_sorted_by_relevance
from .fetch_detailed_contest import fetch_detailed_contest


def generate_template(name: str, in_place: bool = False) -> None:
    project_root_path = Path.cwd() if in_place else Path.cwd().joinpath(name)

    styled_name = text_styling(name, color=Fore.CYAN, style=Style.BRIGHT)
    logger.info(f"start generating template as '{styled_name}'")

    # create directory
    if not in_place and project_root_path.exists():
        logger.error(f"a directory named '{styled_name}' is already exists.")
        return

    try:
        with TemporaryDirectory() as temp_dir:
            project_config = generate_template_helper(name, Path(temp_dir))

            # move to project dir from temp dir
            project_root_path.mkdir()
            for item in os.listdir(temp_dir):
                source_item = os.path.join(temp_dir, item)
                target_item = os.path.join(project_root_path, item)
                shutil.move(source_item, target_item)

    except KeyboardInterrupt:
        print("\n")
        logger.info(text_styling("    -> Keyboard Interrupted", color=Fore.RED))
        logger.info(text_styling("       cleaning...", color=Fore.RED))
        if not in_place and project_root_path.exists():
            shutil.rmtree(project_root_path)
        logger.info(text_styling("       cleaned", color=Fore.RED))
        return

    os.environ["project_root_path"] = str(project_root_path)
    project_config.update_os_environment()

    if environment.global_config.initialize is not None:
        logger.info("exec initialize command...")
        environment.global_config.initialize.exec()


def generate_template_helper(name: str, dest_path: Path) -> ProjectConfig:
    # fetch related contest
    related_contest = ask_related_contest(name)

    # make project config
    project_config = ProjectConfig(project_name=name, contest=related_contest)

    # make config file
    config_file_path = dest_path.joinpath(CONST.CONFIG_FILE_NAME)
    toml.dump(json.loads(project_config.json(exclude_unset=True)), open(config_file_path, mode="w"))

    # append global config
    with open(config_file_path, mode="a") as writer:
        # todo: fetchできるようになったら消す, fetchに失敗したら書いてもいいかも？
        writer.write(
            (
                "\n[contest.environment]\n"
                "# official_visualizer_url = ...\n"
                "# official_tools_url = ...\n"
                '# official_tools_target = "gen vis tester"\n'
                'official_tools_target = "gen vis"\n\n'
            )
        )
        with open(CONST.GLOBAL_CONFIG_FILE_PATH) as reader:
            writer.write("\n#\n# following is a copy of the global config\n#\n\n")
            writer.write(reader.read())

    logger.info(text_styling("CREATION SUCCESSFUL!", color=Fore.GREEN, style=Style.BRIGHT))

    return project_config


def ask_related_contest(name: str, overseas: bool = False) -> Optional[Contest]:
    atcoder_contests = fetch_all_atcoder_heuristic_contests_sorted_by_relevance(name, overseas)
    contest_count = len(atcoder_contests)
    contest_count_digit_len = len(str(contest_count))

    print()
    skipped = False
    target_contest = None
    for th, contest in enumerate(atcoder_contests):
        progress = f"[{th+1:{contest_count_digit_len}d}/{contest_count}] " if th != 0 else ""
        formatted_contest_name = text_styling(contest.name, color=Fore.CYAN, style=Style.BRIGHT)

        replay = input(
            f"{progress}this template will be used for {formatted_contest_name}?  [y(yes) / s(skip) / other(no)]: "
        ).strip()

        # suffix of "yes" is s, which is prefix of "skip"
        if replay.endswith(("y", "yes")):
            target_contest = fetch_detailed_contest(contest)
            break
        elif replay.endswith(("s", "skip")):
            skipped = True
            break

        # todo: adjust to terminal size
        # revert output
        print("\033[1A\033[2K", end="")
        sys.stdout.flush()

    if not skipped and target_contest is None:
        logger.info("No further contest information available...")
    print()


    if target_contest:
        logger.info(
            "this project has been related to the following contest\n"
            "=====================================\n"
            f"{target_contest}\n"
            "=====================================\n"
        )

    return target_contest
