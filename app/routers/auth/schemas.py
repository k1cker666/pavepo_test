from pydantic import BaseModel, EmailStr, Field, AliasChoices, ConfigDict


class YandexUser(BaseModel):
    model_config = ConfigDict(extra='ignore')

    yandex_id: str = Field(validation_alias=AliasChoices("yandex_id", "id"))
    email: EmailStr = Field(validation_alias=AliasChoices("email", "default_email"))
    first_name: str 
    last_name: str
    sex: str

class Credentials(BaseModel):
    username: str
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserSchema(BaseModel):
    model_config = ConfigDict(extra='ignore', from_attributes=True)

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    sex: str