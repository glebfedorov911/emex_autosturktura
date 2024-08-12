import pytest
from httpx import AsyncClient, Cookies

from main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_get_balance():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_balance/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_balance_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_balance/")
    assert response.status_code == 401

# @pytest.mark.asyncio
# async def test_buy_proxy():
#     cookie = Cookies({
#         "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
#     })
#     async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
#         response = await ac.get(f"{settings.api}/proxies/buy_proxy/?count=2&duration=30", cookies=cookie)
#     assert response.status_code == 200

@pytest.mark.asyncio
async def test_buy_proxy_without_money():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/buy_proxy/", cookies=cookie)
    assert response.status_code == 402

@pytest.mark.asyncio
async def test_buy_proxy_with_bad_token():
    cookie = Cookies({
        "access_token": "dasadsdsadsa.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/buy_proxy/", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_buy_proxy_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/buy_proxy/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_list_proxy_group_date():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_group/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_list_proxy_group_date_with_bad_token():
    cookie = Cookies({
        "access_token": "adasddasas.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_group/", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_list_proxy_group_date_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_group/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_proxy_by_date():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_by_date/?date=2024-12-22", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_proxy_by_date_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_by_date/?date=2024-08-24")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_proxy_by_date_with_bad_token():
    cookie = Cookies({
        "access_token": "dsaasddas.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_by_date/?date=2024-08-24", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_proxy_by_date_with_wrong_date():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_by_date/?date=2024-01-24", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_proxy_by_date_with_bad_date():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/get_proxy_by_date/?date=2024-13-24", cookies=cookie)
    assert response.status_code == 405

# @pytest.mark.asyncio
# async def test_prolong_proxy():
#     cookie = Cookies({
#         "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
#     })
#     async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
#         response = await ac.get(f"{settings.api}/proxies/prolong_proxy/?date=2024-08-24&duration=60", cookies=cookie)
#     assert response.status_code == 200

@pytest.mark.asyncio
async def test_prolong_proxy_without_money():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/prolong_proxy/?date=2024-12-22&duration=60", cookies=cookie)
    assert response.status_code == 402

@pytest.mark.asyncio
async def test_prolong_proxy_with_bad_token():
    cookie = Cookies({
        "access_token": "dasdasads.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/prolong_proxy/?date=2024-12-22&duration=60", cookies=cookie)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_prolong_proxy_without_token():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/prolong_proxy/?date=2024-12-22&duration=60")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_prolong_proxy_with_wrong_date():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/prolong_proxy/?date=2025-12-22&duration=60", cookies=cookie)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_prolong_proxy_with_bad_date():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/proxies/prolong_proxy/?date=2024-13-22&duration=60", cookies=cookie)
    assert response.status_code == 405