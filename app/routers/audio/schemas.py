from pydantic import BaseModel, ConfigDict


class AudioUpload(BaseModel):
    name: str


class AudioSchema(AudioUpload):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int
    path: str