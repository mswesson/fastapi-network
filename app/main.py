import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.routes import router

app = FastAPI(title=__name__)


# Обработчик для HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": exc.__class__.__name__,
            "error_message": exc.detail,
        },
    )


# Обработчик для других исключений
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={
            "result": False,
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        },
    )


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
