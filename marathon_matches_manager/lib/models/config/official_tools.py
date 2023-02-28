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

    @validator("setup", always=True)
    def generate_default_setup_command(cls, setup: Any, values):
        if setup is not None:
            return setup
        if "tools_url" not in values:
            return Command(disable=True)
        tools_url: HttpUrl = values["tools_url"]
        targets: List[str] = values["targets"]
        return Command(
            name="setup tools",
            run=[
                f"curl {tools_url} --output tmp.zip",
                "unzip tmp.zip",
                "rm tmp.zip",
                "cd tools",
            ]
            + [f"cargo build --release --bin {target}" for target in targets],
        )
