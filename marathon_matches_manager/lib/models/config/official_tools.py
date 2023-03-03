from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, HttpUrl, validator

from ..command import Command


class OfficialTools(BaseModel):
    tools_url: Optional[HttpUrl] = None
    visualizer_url: Optional[HttpUrl] = None
    tools_path: Optional[Path] = None
    targets: List[str] = []
    setup: Command = None  # type: ignore

    @validator("targets", pre=True)
    def convert_single_target_to_list(cls, target: Any):
        if isinstance(target, str):
            return [target]
        return target

    @validator("setup", always=True, pre=True)
    def generate_default_setup_command(cls, setup: Any, values):
        if values['tools_url'] is None:
            return setup

        tools_url: HttpUrl = values["tools_url"]
        default_run = [
            f"curl {tools_url} --output tmp.zip",
            "unzip tmp.zip",
            "rm tmp.zip",
            "mv tools official_tools",
            "cd ./official_tools; cargo build --release",
        ]

        if setup is None:
            return {'run': default_run}
        elif isinstance(setup, dict) and 'run' not in setup:
            return {**setup, 'run': default_run}
        else:
            return setup

    @validator("setup")
    def set_nop_setup_command(cls, setup: Optional[Command]):
        if setup is None:
            return Command(disable=True)
        else:
            return setup
