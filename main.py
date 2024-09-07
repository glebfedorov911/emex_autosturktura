from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api_v1.path import router
from app.core.add_database import *

import uvicorn


app = FastAPI()
app.include_router(router=router)
# test teeest
origins = [
    "https://forprojectstests.ru",
    "https://fronttest.forprojectstests.ru",
    "http://localhost:5173",
]
#
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
#
if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, host="0.0.0.0", port=8000)
# uvicorn.run(
#     "main:app",
#     reload=False,
#     port=8000,
#     ssl_keyfile="key.pem",
#     ssl_certfile="cert.pem",
# )
# uvicorn.run("main:app", reload=False)

"""uvicorn main:app --reload"""

# 1) исправить баги если они будут (они будут наверное =( )
