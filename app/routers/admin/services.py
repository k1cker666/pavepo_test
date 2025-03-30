from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.auth.models import User

async def make_user_admin(
    session: AsyncSession,
    user: User
):
    user.is_admin = True
    await session.commit()