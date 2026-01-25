from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.v1 import router as v1_router
from core.config import settings
from core.logging_config import logger, api_logger
from core.ai_auth import AIServiceAuthMiddleware, add_rate_limiting_to_app
from utils.exceptions import TaskException

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add rate limiting
limiter = add_rate_limiting_to_app(app)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ultimate-todoflow.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add AI Service Authentication Middleware
app.add_middleware(AIServiceAuthMiddleware)

app.include_router(v1_router, prefix=settings.API_V1_STR)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    api_logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    api_logger.error(f"Validation Error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(TaskException)
async def task_exception_handler(request, exc):
    api_logger.error(f"Task Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    api_logger.error(f"General Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def read_root():
    api_logger.info("Root endpoint accessed")
    return {"message": "Todo API is running!"}


# Function to create tables (for development/testing purposes)
def create_tables():
    from sqlmodel import SQLModel
    from database.session import engine

    # Import all models to register them with SQLModel
    import src.models.user
    import src.models.conversation

    SQLModel.metadata.create_all(engine)
