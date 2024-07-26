from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie

from .schemas import UserCreate, UserUpdate, UserLogin
from app.core.models import db_helper
from . import crud
from .crud import get_payload
from .token_info import TokenInfo
from app.api_v1.auth.utils import encode_jwt
from app.core.models import User    
from .depends import exception_admin    


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/sign_up/")
async def create_user(user_in: UserCreate, session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    exception_admin(payload)

    return await crud.create_user(user_in=user_in, session=session)

@router.post("/login/", response_model=TokenInfo)
async def auth_user(user_log: UserLogin, response: Response, session: AsyncSession = Depends(db_helper.session_depends), access_token: str | None = Cookie(default=None)):
    if access_token:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Вы уже авторизованы | You have already auth"
        )
    user = await crud.validate_user(user_log=user_log, session=session)

    payload = {
        "sub": user.id,
        "username": user.username,
        "description": user.description,
        "fullname": user.fullname,
        "is_admin": user.is_admin
    }

    token = encode_jwt(payload=payload)
    # response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite='Strict')
    response.set_cookie(key="access_token", value=token, httponly=True, samesite='Strict')

    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )

@router.get("/me/")
async def get_me(payload = Depends(get_payload)):
    return payload

@router.get("/logout/")
async def logout(response: Response, access_token: str | None = Cookie(default=None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы | You are not auth"
        )
    response.delete_cookie(key="access_token")
    return {
        "msg": "Вы успешно вышли | Success logout"
    }

@router.get("/show_all/")
async def show_all_users(session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    exception_admin(payload=payload)
    
    return await crud.show_all_users(session=session)

@router.get("/about_one/{user_id}/")
async def about_one_user(user_id: int, session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    exception_admin(payload=payload)

    return await crud.about_one_user(user_id=user_id, session=session)

@router.patch("/edit/{user_id}")
async def edit_user(user_id: int, upd_user: UserUpdate, session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    exception_admin(payload=payload)

    return await crud.edit_user(user_id, upd_user, session)

@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    exception_admin(payload=payload)

    return await crud.delete_user(user_id, session)