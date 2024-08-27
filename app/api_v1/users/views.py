from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Body, Header

from .schemas import UserCreate, UserUpdate, UserLogin
from app.core.models import db_helper
from . import crud
from app.api_v1.auth.utils import get_payload
from .token_info import TokenInfo
from app.api_v1.auth.utils import encode_jwt

from app.core.models import User   
from app.core.config import settings 
from .depends import exception_admin    


router = APIRouter(prefix="/users", tags=["Users"])

# @router.post("/test_sign_without_admin")
# async def create_user(user_in: UserCreate, session: AsyncSession = Depends(db_helper.session_depends)):

#     return await crud.create_user(user_in=user_in, session=session)

@router.post("/sign_up")
async def create_user(user_in: UserCreate, payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends)):
    

    exception_admin(payload)

    return await crud.create_user(user_in=user_in, session=session)

@router.post("/login")#, response_model=TokenInfo)
async def auth_user(user_log: UserLogin, response: Response, access_token: str | None = Header(default=None, convert_underscores=True), session: AsyncSession = Depends(db_helper.session_depends)):
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
    # response.set_cookie(key="access_token", value=token, httponly=False, secure=True, samesite='none',domain="127.0.0.1")
    # response.set_cookie(key="access_token", value=token, httponly=False, samesite='None', secure=True, max_age=settings.auth.access_token_expire_minutes, domain=".forprojectstests.ru")

    # return TokenInfo(
    #     access_token=token,
    #     token_type="Bearer"
    # )
    payload["access_token"] = token
    return payload

# @router.get("/me")
# async def get(payload=Depends(get_payload)):
#     return payload

@router.get("/logout")
async def logout(response: Response, access_token: str | None = Header(default=None, convert_underscores=True)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы | You are not auth"
        )
    #ТЫ ДОЛЖЕН УДАЛИТЬ ТОКЕН
    # response.delete_cookie(key="access_token",domain="127.0.0.1",samesite='none',secure=True,httponly=False)
    # response.delete_cookie(key="access_token",domain=".forprojectstests.ru")
    return {
        "msg": "Вы успешно вышли | Success logout"
    }

@router.get("/show_all")
async def show_all_users(session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    

    exception_admin(payload=payload)
    
    return await crud.show_all_users(session=session)

@router.get("/about_one/{user_id}")
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