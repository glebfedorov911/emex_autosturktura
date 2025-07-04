from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import User 
from app.api_v1.users.schemas import UserOut


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

async def all_information(session: AsyncSession):
    stmt = select(User.id, User.username, User.fullname, User.description, User.is_admin, User.is_parsing)
    result: Result = await session.execute(stmt)
    users = result.fetchall()

    return [UserOut(id=user[0], username=user[1], fullname=user[2], description=user[3], is_admin=user[4], is_parsing=user[5]) for user in users]

async def check_username(session: AsyncSession, username: str, user_id: int):
    stmt = select(User.username).where(User.username == username).where(User.id != user_id)
    result: Result = await session.execute(stmt)
    if not result.scalar() is None:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Данное имя уже используется"
        )