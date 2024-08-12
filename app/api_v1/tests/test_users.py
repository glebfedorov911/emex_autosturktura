import pytest
from httpx import AsyncClient, Cookies

from main import app
from app.core.config import settings
from app.api_v1.users.schemas import UserCreate, UserLogin, UserUpdate


@pytest.mark.asyncio
async def test_me():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/me/", cookies=cookie)
    assert response.status_code == 200
    assert response.json() == {"sub":4,"username":"string","description":"string","fullname":"string","is_admin":True}

@pytest.mark.asyncio
async def test_me_without_cookie():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/me/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Ошибка токена | Token error"}

@pytest.mark.asyncio
async def test_me_with_bad_token():
    cookie = Cookies({
        "access_token": "dasadsdas.dasdsadas.asddas-sdads--asddsadsa-ads-ads-adsasd-dasdas"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/me/", cookies=cookie)
    assert response.status_code == 401
    assert response.json() == {"detail": "Ошибка токена | Token error"}

@pytest.mark.asyncio
async def test_create_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    username = "st12"
    description = "st1"
    fullname = "st1"
    is_admin = False
    password = "st1"

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserCreate(username=username, fullname=description, password=password, is_admin=is_admin, description=description).model_dump()
        response = await ac.post(f"{settings.api}/users/sign_up/", json=user_data, cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_user_not_admin():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUsInVzZXJuYW1lIjoic3RyaW5nMzMzIiwiZGVzY3JpcHRpb24iOiJzdHJpbmczMzMiLCJmdWxsbmFtZSI6InN0cmluZzMzMyIsImlzX2FkbWluIjpmYWxzZX0.B7pIR5WmcXH15T3v8btVzB5sXADMZRgMqcfoWbEJHTk8MzyZ_yE7NK4HB69ru1QIbMk2RutnFMWIJYwIsSOdHSFx_rKKa1ECi1bYeMCcNGZtnW4sk6Z8qSTY13rF0gBbi2_6ZkOW7HYKMmf4k5c2WjdgOjzxVahnZqjGyzxj73lRQ5PRiFWdDVZQDmSVgFf9Xx9BMBm658xQUt-VRD8lI3411WMahMnsod2SgeufBvPaiFOMLyFOHkLa9fj9f40u-qBo4MHpQPGnBXqSIvxUFrk0WIL9-UZkqOlKdOAw3VlYwgYQTzVqw_VUmLcrec8w-XXjDYcQcE3fSbHlztgv9w"
    })
    username = "st12"
    description = "st1"
    fullname = "st1"
    is_admin = False
    password = "st1"

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserCreate(username=username, fullname=description, password=password, is_admin=is_admin, description=description).model_dump()
        response = await ac.post(f"{settings.api}/users/sign_up/", json=user_data, cookies=cookie)
    assert response.status_code == 403
    assert response.json() == {"detail": "Недостаточно прав | Not enough rights"}

@pytest.mark.asyncio
async def test_create_user_not_valid_token():
    cookie = Cookies({
        "access_token": "dasadsdas.dasdsadas.asddas-sdads--asddsadsa-ads-ads-adsasd-dasdas"
    })
    username = "st1"
    description = "st1"
    fullname = "st1"
    is_admin = False
    password = "st1"

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserCreate(fullname=username, description=description, username=fullname, is_admin=is_admin, password=password).model_dump()
        response = await ac.post(f"{settings.api}/users/sign_up/", cookies=cookie, json=user_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Ошибка токена | Token error"}

@pytest.mark.asyncio
async def test_create_user_already_name():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    username = "st1"
    description = "st1"
    fullname = "st1"
    is_admin = False
    password = "st1"

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserCreate(fullname=username, description=description, username=fullname, is_admin=is_admin, password=password).model_dump()
        response = await ac.post(f"{settings.api}/users/sign_up/", cookies=cookie, json=user_data)
    assert response.status_code == 409
    assert response.json() == {"detail": "Данное имя уже используется | This username already exists"}

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserLogin(username="string", password="string").model_dump()
        response = await ac.post(f"{settings.api}/users/login/", json=user_data)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_already_auth():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserLogin(username="string", password="string").model_dump()
        response = await ac.post(f"{settings.api}/users/login/", cookies=cookie, json=user_data)
    assert response.status_code == 405
    assert response.json() == {"detail": "Вы уже авторизованы | You have already auth"}

@pytest.mark.asyncio
async def test_login_already_auth_wrong_token():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.adsasdadsadsdsa.asdsdadas-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserLogin(username="string", password="string").model_dump()
        response = await ac.post(f"{settings.api}/users/login/", cookies=cookie, json=user_data)
    assert response.status_code == 405
    assert response.json() == {"detail": "Вы уже авторизованы | You have already auth"}

@pytest.mark.asyncio
async def test_login_unknown_name():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserLogin(username="randaifdfhjdjdsfjsdf", password="string").model_dump()
        response = await ac.post(f"{settings.api}/users/login/", json=user_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Неизвестный логин | unknown username"}

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = UserLogin(username="string", password="dasdasadsdas").model_dump()
        response = await ac.post(f"{settings.api}/users/login/", json=user_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Неправильный пароль | wrong password"}

@pytest.mark.asyncio
async def test_logout():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/logout/", cookies=cookie)

    assert response.status_code == 200
    assert response.json() == {"msg": "Вы успешно вышли | Success logout"}

@pytest.mark.asyncio
async def test_logout_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/logout/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Вы не авторизованы | You are not auth"}

@pytest.mark.asyncio
async def test_show_all_users():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/show_all/", cookies=cookie)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_show_all_users_wrong_token():
    cookie = Cookies({
        "access_token": "dasadsdassd.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/show_all/", cookies=cookie)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_show_all_users_token_without_access():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUsInVzZXJuYW1lIjoic3RyaW5nMzMzIiwiZGVzY3JpcHRpb24iOiJzdHJpbmczMzMiLCJmdWxsbmFtZSI6InN0cmluZzMzMyIsImlzX2FkbWluIjpmYWxzZX0.B7pIR5WmcXH15T3v8btVzB5sXADMZRgMqcfoWbEJHTk8MzyZ_yE7NK4HB69ru1QIbMk2RutnFMWIJYwIsSOdHSFx_rKKa1ECi1bYeMCcNGZtnW4sk6Z8qSTY13rF0gBbi2_6ZkOW7HYKMmf4k5c2WjdgOjzxVahnZqjGyzxj73lRQ5PRiFWdDVZQDmSVgFf9Xx9BMBm658xQUt-VRD8lI3411WMahMnsod2SgeufBvPaiFOMLyFOHkLa9fj9f40u-qBo4MHpQPGnBXqSIvxUFrk0WIL9-UZkqOlKdOAw3VlYwgYQTzVqw_VUmLcrec8w-XXjDYcQcE3fSbHlztgv9w"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/show_all/", cookies=cookie)

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_about_one_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/about_one/{1}/", cookies=cookie)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_about_one_user_wrong_token():
    cookie = Cookies({
        "access_token": "dsaadsasd.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/about_one/{1}/", cookies=cookie)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_about_one_user_without_access():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUsInVzZXJuYW1lIjoic3RyaW5nMzMzIiwiZGVzY3JpcHRpb24iOiJzdHJpbmczMzMiLCJmdWxsbmFtZSI6InN0cmluZzMzMyIsImlzX2FkbWluIjpmYWxzZX0.B7pIR5WmcXH15T3v8btVzB5sXADMZRgMqcfoWbEJHTk8MzyZ_yE7NK4HB69ru1QIbMk2RutnFMWIJYwIsSOdHSFx_rKKa1ECi1bYeMCcNGZtnW4sk6Z8qSTY13rF0gBbi2_6ZkOW7HYKMmf4k5c2WjdgOjzxVahnZqjGyzxj73lRQ5PRiFWdDVZQDmSVgFf9Xx9BMBm658xQUt-VRD8lI3411WMahMnsod2SgeufBvPaiFOMLyFOHkLa9fj9f40u-qBo4MHpQPGnBXqSIvxUFrk0WIL9-UZkqOlKdOAw3VlYwgYQTzVqw_VUmLcrec8w-XXjDYcQcE3fSbHlztgv9w"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/about_one/{1}/", cookies=cookie)
    
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_about_one_user_unknown_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/users/about_one/{9999999999}/", cookies=cookie)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_edit_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = {"fullname": "gleb"}
        response = await ac.patch(url=f"{settings.api}/users/edit/1", json=user_data, cookies=cookie)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_edit_user_wrong_token():
    cookie = Cookies({
        "access_token": "dasasdasdasdsads.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = {"fullname": "gleb"}
        response = await ac.patch(url=f"{settings.api}/users/edit/1", json=user_data, cookies=cookie)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_edit_user_without_access():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUsInVzZXJuYW1lIjoic3RyaW5nMzMzIiwiZGVzY3JpcHRpb24iOiJzdHJpbmczMzMiLCJmdWxsbmFtZSI6InN0cmluZzMzMyIsImlzX2FkbWluIjpmYWxzZX0.B7pIR5WmcXH15T3v8btVzB5sXADMZRgMqcfoWbEJHTk8MzyZ_yE7NK4HB69ru1QIbMk2RutnFMWIJYwIsSOdHSFx_rKKa1ECi1bYeMCcNGZtnW4sk6Z8qSTY13rF0gBbi2_6ZkOW7HYKMmf4k5c2WjdgOjzxVahnZqjGyzxj73lRQ5PRiFWdDVZQDmSVgFf9Xx9BMBm658xQUt-VRD8lI3411WMahMnsod2SgeufBvPaiFOMLyFOHkLa9fj9f40u-qBo4MHpQPGnBXqSIvxUFrk0WIL9-UZkqOlKdOAw3VlYwgYQTzVqw_VUmLcrec8w-XXjDYcQcE3fSbHlztgv9w"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = {"fullname": "gleb"}
        response = await ac.patch(url=f"{settings.api}/users/edit/1", json=user_data, cookies=cookie)

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_edit_user_unknown_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        user_data = {"fullname": "gleb"}
        response = await ac.patch(url=f"{settings.api}/users/edit/99999999", json=user_data, cookies=cookie)

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(url=f"{settings.api}/users/delete/6", cookies=cookie)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_user_wrong_token():
    cookie = Cookies({
        "access_token": "dasasdasdasdsads.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(url=f"{settings.api}/users/delete/1", cookies=cookie)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_user_without_access():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjUsInVzZXJuYW1lIjoic3RyaW5nMzMzIiwiZGVzY3JpcHRpb24iOiJzdHJpbmczMzMiLCJmdWxsbmFtZSI6InN0cmluZzMzMyIsImlzX2FkbWluIjpmYWxzZX0.B7pIR5WmcXH15T3v8btVzB5sXADMZRgMqcfoWbEJHTk8MzyZ_yE7NK4HB69ru1QIbMk2RutnFMWIJYwIsSOdHSFx_rKKa1ECi1bYeMCcNGZtnW4sk6Z8qSTY13rF0gBbi2_6ZkOW7HYKMmf4k5c2WjdgOjzxVahnZqjGyzxj73lRQ5PRiFWdDVZQDmSVgFf9Xx9BMBm658xQUt-VRD8lI3411WMahMnsod2SgeufBvPaiFOMLyFOHkLa9fj9f40u-qBo4MHpQPGnBXqSIvxUFrk0WIL9-UZkqOlKdOAw3VlYwgYQTzVqw_VUmLcrec8w-XXjDYcQcE3fSbHlztgv9w"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(url=f"{settings.api}/users/delete/1", cookies=cookie)

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_user_unknown_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(url=f"{settings.api}/users/delete/99999999", cookies=cookie)

    assert response.status_code == 404