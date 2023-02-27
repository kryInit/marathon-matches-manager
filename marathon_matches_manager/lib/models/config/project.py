import dataclasses


@dataclasses.dataclass
class Project:
    name: str
    default_working_directory: str

    def __init__(self, project_dict: dict):
        pass
