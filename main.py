from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api_v1.path import router

import uvicorn


app = FastAPI()
app.include_router(router=router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False) 
 
'''uvicorn main:app --reload'''

# 1) исправить баги если они будут (они будут наверное =( )