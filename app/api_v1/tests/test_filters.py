import pytest
from httpx import AsyncClient, Cookies

from main import app
from app.core.config import settings
from app.api_v1.filters.schemas import FilterCreate, FilterUpdate


@pytest.mark.asyncio
async def test_create_filter():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        new_filter = FilterCreate(is_has_logo=True, is_has_brand=True, is_bigger_then_date=True, logo="LOGO", brand="BRAND", date=5)
        response = await ac.post(f"{settings.api}/filters/create_filter/", json=new_filter.model_dump(), cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_filter_with_bad_cookie():
    cookie = Cookies({
        "access_token": "bad_cookie"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        new_filter = FilterCreate(is_has_logo=True, is_has_brand=True, is_bigger_then_date=True, logo="LOGO", brand="BRAND", date=5)
        response = await ac.post(f"{settings.api}/filters/create_filter/", json=new_filter.model_dump(), cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_filter_without_cookie():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        new_filter = FilterCreate(is_has_logo=True, is_has_brand=True, is_bigger_then_date=True, logo="LOGO", brand="BRAND", date=5)
        response = await ac.post(f"{settings.api}/filters/create_filter/", json=new_filter.model_dump())
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_filters():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filters/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_filters_with_bad_cookies():
    cookie = Cookies({
        "access_token": "bad_cookies"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filters/", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_filters_without_cookies():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filters/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_filter():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filter/6", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_filter_with_bad_cookies():
    cookie = Cookies({
        "access_token": "bad_cookies"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filter/2", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_filter_without_cookies():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filter/2")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_filter_with_bad_id():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filter/22", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_filter_not_my_id():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/filters/get_filter/1", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_edit_filter():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        edit_filter = {"brand": "new222"}
        response = await ac.patch(f"{settings.api}/filters/edit_filter/6", json=edit_filter, cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_edit_filter_not_my_id():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        edit_filter = FilterUpdate(brand="new")
        response = await ac.patch(f"{settings.api}/filters/edit_filter/1", json=edit_filter.model_dump(), cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_edit_filter_with_bad_id():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        edit_filter = FilterUpdate(brand="new")
        response = await ac.patch(f"{settings.api}/filters/edit_filter/22", json=edit_filter.model_dump(), cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_edit_filter_with_bad_cookie():
    cookie = Cookies({
        "access_token": "bad_cookie"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        edit_filter = FilterUpdate(brand="new")
        response = await ac.patch(f"{settings.api}/filters/edit_filter/2", json=edit_filter.model_dump(), cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_edit_filter_without_cookie():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        edit_filter = FilterUpdate(brand="new")
        response = await ac.patch(f"{settings.api}/filters/edit_filter/2", json=edit_filter.model_dump())
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_filter():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(f"{settings.api}/filters/delete_filter/9", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_filter_with_bad_token():
    cookie = Cookies({
        "access_token": "bad_token"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(f"{settings.api}/filters/delete_filter/5", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_filter_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(f"{settings.api}/filters/delete_filter/5")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_filter_with_bad_id():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(f"{settings.api}/filters/delete_filter/131231", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_filter_with_not_my_id():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.delete(f"{settings.api}/filters/delete_filter/1", cookies=cookie)
    assert response.status_code == 404