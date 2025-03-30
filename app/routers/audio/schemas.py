from pydantic import BaseModel


class AudioSchema(BaseModel):
    id: int
    name: str
    path: str
