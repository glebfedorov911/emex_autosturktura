import pytest
from httpx import AsyncClient, Cookies

from main import app
from app.core.config import settings
from app.api_v1.files.schemas import FilesCreate


@pytest.mark.asyncio
async def test_upload_file():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        with open('app/upload_file/shablon.xlsx', 'rb') as file:
            content = {"file": file.read()}
        response = await ac.post(f"{settings.api}/files/upload_file/", files=content, cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_upload_bad_file():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        with open('app/upload_file/bad_file.xlsx', 'rb') as file:
            content = {"file": file.read()}
        response = await ac.post(f"{settings.api}/files/upload_file/", files=content, cookies=cookie)
    assert response.status_code == 405

@pytest.mark.asyncio
async def test_upload_file_with_bad_cookie():
    cookie = Cookies({
        "access_token": "bad_cookie"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        with open('app/upload_file/shablon.xlsx', 'rb') as file:
            content = {"file": file.read()}
        response = await ac.post(f"{settings.api}/files/upload_file/", files=content, cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_upload_file_without_cookie():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        with open('app/upload_file/shablon.xlsx', 'rb') as file:
            content = {"file": file.read()}
        response = await ac.post(f"{settings.api}/files/upload_file/", files=content)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_download_file():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.post(f"{settings.api}/files/download_file/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_download_file_with_bad_cookie():
    cookie = Cookies({
        "access_token": "bad_cookie"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.post(f"{settings.api}/files/download_file/", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_download_file_without_cookie():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.post(f"{settings.api}/files/download_file/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/before_parsing/2", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_before_parsing_with_bad_cookies():
    cookie = Cookies({
        "access_token": "bad_cookies"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/before_parsing/2", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing_without_cookies():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/before_parsing/2")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing_with_another_user_token_for_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/before_parsing/1", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_before_parsing_with_bad_token_for_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/before_parsing/2312131", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_before_parsing():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/after_parsing/2", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_before_parsing_with_bad_cookies():
    cookie = Cookies({
        "access_token": "bad_cookies"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/after_parsing/2", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing_without_cookies():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/after_parsing/2")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing_with_another_user_token_for_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/after_parsing/1", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_before_parsing_with_bad_token_for_user():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.post(f"{settings.api}/files/download_file/after_parsing/2312131", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_before_parsing():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoic3RyaW5nX2FkbWluX2Nvb2wiLCJkZXNjcmlwdGlvbiI6ImphbSIsImZ1bGxuYW1lIjoiZ2xlYiIsImlzX2FkbWluIjp0cnVlfQ.SdNH5_TggvwaLEda6eqGFfvSYjLTQby9v20X08HXwaQJhppEF7jZ2bfnPVZ_jxMDaJOcag_TiJ_aNcQ69-_i47A9ZHfSztTk6BZY3keCsKlusSqZ983QV1gYml0iK4uXZ4pqAFBo1RnSW4tVqqJpGC9bU-wJ2fRsyO0EF6Tpwt0go9wdqBhiHKVaZS-FZNKyYr_MgwFUsUOmCBwPBcForRyXDHexJtcXTYAQhgNKeROfh0EdcXeBJ-GBLEdRDPZQp4byctXCF_50jdjohEIxRra0CIOPlSTILcgL5b6ORyMGeBS9tRnAceAZyEuHWsHDXCIgdJu0lMwRDpHg5FAJow"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.get(f"{settings.api}/files/all_files/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_before_parsing_with_bad_cookies():
    cookie = Cookies({
        "access_token": "bad_cookies"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.get(f"{settings.api}/files/all_files/", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing_without_cookies():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.get(f"{settings.api}/files/all_files/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_before_parsing():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000", follow_redirects=True) as ac:
        response = await ac.get(f"{settings.api}/files/get_shablon/")
    assert response.status_code == 200