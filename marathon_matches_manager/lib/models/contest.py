from datetime import datetime, timedelta

from pydantic import BaseModel, HttpUrl, validator


class Contest(BaseModel):
    url: HttpUrl
    name: str
    sub_name: str
    start_time: datetime
    time_limit: timedelta
    is_rated: str

    @validator("time_limit")
    def scale_time_limit(cls, time_limit: timedelta):
        # 01:40 is 1 hour 40 minutes in atcoder
        # but pydantic recognize it as 1 minute 40 seconds
        return time_limit * 60

    def __str__(self):
        return (
            f"url          : {self.url}\n"
            f"contest name : {self.name}\n"
            f"    sub name : {self.sub_name}\n"
            f"start time   : {self.start_time}\n"
            f"time limit   : {self.time_limit}\n"
            f"is rated     : {self.is_rated}"
        )
