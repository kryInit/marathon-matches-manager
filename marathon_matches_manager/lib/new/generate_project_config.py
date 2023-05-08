from ..models import ProjectConfig, Contest, Project, OfficialTools
from typing import Optional


def generate_project_config(name: str, contest: Optional[Contest]) -> ProjectConfig:
    # doto fetch official tools url and generate OfficialTools
    return ProjectConfig(
        project=Project(name=name),
        contest=contest,
        official_tools=None
    )
