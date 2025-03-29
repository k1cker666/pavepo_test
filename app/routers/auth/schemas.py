from pydantic import BaseModel, EmailStr, Field, AliasChoices, ConfigDict


class YandexUser(BaseModel):
    model_config = ConfigDict(extra='ignore')

    yandex_id: str = Field(validation_alias=AliasChoices("yandex_id", "id"))
    email: EmailStr = Field(validation_alias=AliasChoices("email", "default_email"))
    first_name: str 
    last_name: str
    sex: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"