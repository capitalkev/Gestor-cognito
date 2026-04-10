from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interface.routers import usuarios

def create_application() -> FastAPI:
    app = FastAPI(
        title="Identity Service - Capital Express",
        description="Microservicio IAM para administrar usuarios en AWS Cognito",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(usuarios.router)

    return app

app = create_application()