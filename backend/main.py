"""FastAPI application for Lagoa, a personal AI assistant.

Wires together the auth, chat and model endpoints. Each user has several
chats; every chat keeps its own history and a running summary of older
messages so the model keeps context.
"""

from dataclasses import asdict

from fastapi import FastAPI
from db import Base, engine
from ai.setup import registry
from auth import router as auth_router
from chats import router as chats_router
from schemas import ModelsResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the database tables on application startup."""
    Base.metadata.create_all(engine)
    print("All tabels created!")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Lagoa"
    )
app.include_router(auth_router)
app.include_router(chats_router)


@app.get("/models")
def get_models() -> ModelsResponse:
    """Return the models users can pick and the default one."""
    return ModelsResponse(
        default=registry.default_id,
        models=[asdict(info) for info in registry.models()],
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )
