import pytest
from httpx import AsyncClient, Cookies

from main import app
from app.core.config import settings
from app.api_v1.parser.schemas import ParserCreate


@pytest.mark.asyncio
async def test_start_parser():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/parser/start/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_stop_parser():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/parser/stop/", cookies=cookie)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_status_parser():
    cookie = Cookies({
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
    })
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get(f"{settings.api}/parser/status_check/", cookies=cookie)
    assert response.status_code == 200

# #если нет файлов
# @pytest.mark.asyncio
# async def test_upload_file_without_file():
#     cookie = Cookies({
#         "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
#     })
#     async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
#         response = await ac.get(f"{settings.api}/parser/start/", cookies=cookie)
#     assert response.status_code == 405

# @pytest.mark.asyncio
# async def test_stop_parser_without_thread():
#     cookie = Cookies({
#         "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQsInVzZXJuYW1lIjoic3RyaW5nIiwiZGVzY3JpcHRpb24iOiJzdHJpbmciLCJmdWxsbmFtZSI6InN0cmluZyIsImlzX2FkbWluIjp0cnVlfQ.Xa5i_JUNp43o1GjZkpuN1TNvxbfFd-k9rL3NMiOXfTLQ8zT--YT57Sxo8QOls4Nm2T9sBGDlozvZ0xPIMaDrdOgC6ZNDvf4imhNEP8t6Bks5U__sZ3AIzheumbxoYCstDnbxdaPsv2Y2gKfjNnaN6sZudZ4aOZrk0aFQm-369ehYlzY2nkb2e4kRRGy-GFtLAV2fJoJxJpoLCYkSCeH_uW7ddQuTKyFinecRao0V8Z63QBSpUidnARCzAQxZAP8X0L1s05u9rsAAq9KVQRVL4GW020CMYABuAxQT2n2RHm6zSBr1_lx1EEXpgVu9U-5BQwRz-9h20AjsSiNCek9EGQ"
#     })
#     async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
#         response = await ac.get(f"{settings.api}/parser/stop/", cookies=cookie)
#     assert response.status_code == 404