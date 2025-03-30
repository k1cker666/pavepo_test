from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserUpdate(BaseModel):
    model_config = ConfigDict()

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None