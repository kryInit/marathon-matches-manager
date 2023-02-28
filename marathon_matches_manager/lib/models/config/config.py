from typing import Optional

from pydantic import BaseModel

from ..contest import Contest
from .official_tools import OfficialTools
from .project import Project


class ProjectConfig(BaseModel):
    project: Project
    contest: Optional[Contest]
    official_tools: Optional[OfficialTools]
