import dataclasses


@dataclasses.dataclass
class Contest:
    url: str
    name: str
    sub_name: str
    start_time: str
    time_limit: str
    is_rated: str

    def __str__(self):
        return (
            f"url          : {self.url}\n"
            f"contest name : {self.name}\n"
            f"    sub name : {self.sub_name}\n"
            f"start time   : {self.start_time}\n"
            f"time limit   : {self.time_limit}\n"
            f"is rated     : {self.is_rated}"
        )
