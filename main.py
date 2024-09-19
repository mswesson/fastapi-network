import uvicorn
from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

app = FastAPI(title=__name__)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
