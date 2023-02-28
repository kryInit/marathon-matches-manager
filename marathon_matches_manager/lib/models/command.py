from datetime import timedelta
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel, validator


class Command(BaseModel):
    name: str = "Untitled Command"
    run: List[str] = []
    working_directory: Path = Path("${PROJECT_ROOT_PATH}")
    disable: bool = False
    timeout: timedelta = timedelta(seconds=300)

    @validator("run", pre=True)
    def convert_single_run_cmd_to_list(cls, run: Any):
        if isinstance(run, str):
            return [run]
        return run
