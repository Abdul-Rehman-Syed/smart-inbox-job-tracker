from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.email import router as email_router
from app.routes.jobs import router as jobs_router
from app.schemas import ApiResponse, Health

settings = get_settings()

app = FastAPI(
    title="Job Tracker API",
    description="FastAPI backend for a portfolio-ready job application tracker.",
    version="1.0.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(email_router)
app.include_router(jobs_router)


@app.on_event("startup")
def on_startup():
    if settings.environment in {"development", "test"}:
        Base.metadata.create_all(bind=engine)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "data": None, "message": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        sanitized = dict(error)
        if "ctx" in sanitized:
            sanitized["ctx"] = {key: str(value) for key, value in sanitized["ctx"].items()}
        errors.append(sanitized)
    return JSONResponse(
        status_code=422,
        content={"success": False, "data": None, "message": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    if settings.debug:
        message = str(exc)
    else:
        message = "Internal server error"
    return JSONResponse(status_code=500, content={"success": False, "data": None, "message": message})


@app.get("/api/health", response_model=ApiResponse[Health])
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return ApiResponse(data=Health(status="ok", environment=settings.environment, database="reachable"))
