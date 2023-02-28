import logging
import os
import subprocess

from ..models.config import ProjectConfig


def setup_official_tools(config: ProjectConfig) -> None:
    logger = logging.getLogger(__name__)
    if config.official_tools is None:
        logger.error("configuration of official official_tools doesn't exist in m3-config.toml")
        return

    if config.official_tools.setup.disable:
        logger.warning("official official_tools setup command is disabled.")
        return

    setup_command = config.official_tools.setup
    logger.info(f"run command '{setup_command.name}'")
    for cmd in setup_command.run:
        logger.info(f"run: {cmd}")
        subprocess.run(
            cmd,
            shell=True,
            timeout=setup_command.timeout.seconds,
            cwd=os.path.expandvars(setup_command.working_directory),
        )
