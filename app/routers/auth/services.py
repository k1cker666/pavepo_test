from app.settings import settings


def get_data_for_token_request(code: str):
    return {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.yandex.client_id,
        "client_secret": settings.yandex.client_secret,
    }