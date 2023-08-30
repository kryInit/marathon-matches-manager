import os
import subprocess

from logzero import logger

from ..misc import environment
from ..models import Command


def exec_command_by_name(command_name: str):
    # todo: localとglobalどうしようかな
    if command_name not in environment.project_config.commands:
        logger.error(f"this command is not found: {command_name}")

    command = environment.project_config.commands[command_name]
    command.exec()
