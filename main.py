from fastapi import FastAPI

from app.api_v1.path import router

import uvicorn


app = FastAPI()
app.include_router(router=router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True) 
 
'''uvicorn main:app --reload'''