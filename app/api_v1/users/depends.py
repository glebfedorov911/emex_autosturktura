from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User 


def exception_admin(payload):
    if not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав | Not enough rights"
        )

def unknown_user(user):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Неизвестный логин | unknown username"
        )

async def get_user_by_id(user_id: int, session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result: Result = await session.execute(stmt)
    user = result.scalar()

    return user