from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class YandexToken:
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str
