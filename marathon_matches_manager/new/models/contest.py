import dataclasses


@dataclasses.dataclass
class Contest:
    name: str
    sub_name: str
    start_time: str
    period: str
    rated: str

    def __str__(self):
        return (
            f"contest name : {self.name}\n"
            f"    sub name : {self.sub_name}\n"
            f"start time   : {self.start_time}\n"
            f"period       : {self.period}\n"
            f"rated        : {self.rated}"
        )
