from typing import Optional

from ..models import BaseConfig, Contest, ProjectConfig


def generate_project_config(name: str, contest: Optional[Contest]) -> ProjectConfig:
    # doto fetch official tools url and generate OfficialTools
    return ProjectConfig(
        project_name=name,
        contest=contest,
    )
