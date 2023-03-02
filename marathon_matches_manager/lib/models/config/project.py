from pathlib import Path

from pydantic import BaseModel


class Project(BaseModel):
    name: str = "Untitled Project"
    default_working_directory: Path = Path("${PROJECT_ROOT_PATH}")
