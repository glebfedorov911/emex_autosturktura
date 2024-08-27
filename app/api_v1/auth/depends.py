from app.api_v1.users.crud import get_payload


async def check_payload(access_token: str):
    try:
        payload = await get_payload(access_token=access_token)
    except Exception as e:
        raise e

    return payload