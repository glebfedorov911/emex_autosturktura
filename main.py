from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api_v1.path import router
from app.core.add_database import *

import uvicorn


app = FastAPI()
app.include_router(router=router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1",
    # "http://forprojectstests.ru",
    # "http://api.forprojectstests.ru",
    "https://localhost",
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "https://127.0.0.1:5173",
    "https://127.0.0.1","http://localhost:5173",
    "https://forprojectstests.ru",
    # "https://api.forprojectstests.ru",
]
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

# if __name__ == "__main__":
#     # uvicorn.run("main:app", reload=False, host="0.0.0.0", port=8000) 
#     uvicorn.run("main:app", reload=False,  port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem") 
#     # uvicorn.run("main:app", reload=False) 
 
'''uvicorn main:app --reload'''

# 1) исправить баги если они будут (они будут наверное =( )