# index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .empleados import router as empleado_router
from .auth import router as auth_router

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(empleado_router)
    app.include_router(auth_router)

    return app

app = create_app()