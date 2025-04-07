
from pydantic import BaseModel, ConfigDict


class UserUpdate(BaseModel):
    model_config = ConfigDict()

    first_name: str | None = None
    last_name: str | None = None
    sex: str | None = None
