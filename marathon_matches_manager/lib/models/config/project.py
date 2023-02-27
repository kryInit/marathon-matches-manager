from pathlib import Path

from pydantic import BaseModel

from ...utils import snake2kebab


class Project(BaseModel):
    name: str = "Untitled Project"
    default_working_directory: Path = Path("${PROJECT_ROOT_PATH}")

    class Config:
        alias_generator = snake2kebab
