from logzero import logger

from marathon_matches_manager.lib.misc import environment


def exec_command_by_name(command_name: str):
    # todo: localとglobalどうしようかな
    if command_name not in environment.project_config.commands:
        logger.error(f"this command is not found: {command_name}")

    environment.project_config.commands[command_name].exec()
