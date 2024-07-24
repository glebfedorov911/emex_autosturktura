from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status, Cookie
from fastapi.security import HTTPBearer

from jwt.exceptions import InvalidTokenError

from .schemas import UserCreate, UserUpdate, UserLogin
from core.models import User        
from api_v1.auth.utils import hash_password, validate_password
from .depends import unknown_user, get_user_by_id
from api_v1.auth.utils import decode_jwt


http_bearer = HTTPBearer()

async def get_payload(access_token: str | None = Cookie(default=None)):

    try:
        payload = decode_jwt(
            token=access_token
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка токена | Token error"
        )

    return payload

async def create_user(user_in: UserCreate, session: AsyncSession):
    try:
        hashed_password = hash_password(password=user_in.password)

        new_user = User(**user_in.model_dump())
        new_user.password = hashed_password
        session.add(new_user)
        await session.commit()

        return new_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Данное имя уже используется | This surname already exists"
        )

async def validate_user(user_log: UserLogin, session: AsyncSession):
    stmt = select(User).where(User.username == user_log.username)
    result: Result = await session.execute(stmt)
    user = result.scalar()

    unknown_user(user)

    if not validate_password(user_log.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Неправильный пароль | wrong password"
        )

    return user

async def show_all_users(session: AsyncSession):
    stmt = select(User)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    for user in users:
        del user.password

    return users

async def edit_user(user_id: int, upd_user: UserUpdate, session: AsyncSession):
    user = await get_user_by_id(user_id=user_id, session=session)

    unknown_user(user)

    update_user = upd_user.dict(exclude_unset=True)
    update_user["password"] = hash_password(update_user["password"])

    for key, value in update_user.items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()

    return user

async def about_one_user(user_id: int, session: AsyncSession):
    user = await get_user_by_id(user_id=user_id, session=session)
    
    unknown_user(user)
    del user.password

    return user

async def delete_user(user_id: int, session: AsyncSession):
    user = await get_user_by_id(user_id=user_id, session=session)
    
    unknown_user(user)
    await session.delete(user)
    await session.commit()

    return {
        "message": "Пользователь удален | User is deleted"
    }