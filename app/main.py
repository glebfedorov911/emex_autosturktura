from fastapi import FastAPI

import uvicorn


app = FastAPI()

@app.get("/")
def index(name: str | None = "World"):
    return {
        "message": f"Hello, {name.capitalize()}!"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

