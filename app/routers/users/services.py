from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.auth.models import User
from app.routers.users.schemas import UserUpdate


async def update_user(session: AsyncSession, user: User, user_update: UserUpdate) -> User:
    data_to_update = user_update.model_dump(exclude_unset=True)
    for key, value in data_to_update.items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user
