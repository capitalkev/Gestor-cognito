from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.interface.middleware.api_key_auth import ApiKeyMiddleware
from src.interface.routers import health, usuarios


def create_application() -> FastAPI:
    app = FastAPI(
        title="Identity Service - Capital Express",
        description="Microservicio IAM para administrar usuarios en AWS Cognito",
        version="1.0.0",
    )
    app.add_middleware(ApiKeyMiddleware, api_keys=settings.parsed_api_keys)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "https://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(usuarios.router)

    return app


app = create_application()
