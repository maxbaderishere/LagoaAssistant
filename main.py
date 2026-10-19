"""FastAPI application for Lagoa, a personal AI assistant.

Exposes the auth and chat endpoints, keeps each user's conversation history in
the database and maintains a running summary of older messages so the model
keeps context.
"""

from fastapi import FastAPI, Body
from db import Base, add_request_data, engine, get_summary, get_unsummarized_requests, get_user_requests, save_summary
from ai import Client, GeminiClient, GroqClient
from auth import CurrentUser, router as auth_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from config import cfg

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

#client: Client = GeminiClient(api_key=cfg.gemini_api_key)
client: Client = GroqClient(api_key=cfg.groq_api_key)


def update_summary(user_id: int) -> None:
    """Fold old messages of a user into their conversation summary.

    The last ``cfg.keep_last`` messages are always left out, because they are
    sent to the model verbatim. The summary is only updated once at least
    ``cfg.summarise_every`` older messages have piled up, so the extra model
    call doesn't happen on every request.

    Args:
        user_id: Id of the user whose summary to update.
    """
    summary = get_summary(user_id=user_id)
    old_text = summary.text if summary else ""
    last_id = summary.last_summarized_id if summary else 0

    new_messages = get_unsummarized_requests(user_id=user_id, after_id=last_id)
    to_summarise = new_messages[:-cfg.keep_last]
    if len(to_summarise) < cfg.summarise_every:
        return

    new_text = client.summarise(old_text, to_summarise)
    save_summary(user_id=user_id, text=new_text, last_summarized_id=to_summarise[-1].id)

@app.get("/requests")
def get_requests(user: CurrentUser):
    """Return the full chat history of the signed-in user, oldest first."""
    return get_user_requests(user_id=user.id)


@app.post("/requests")
def send_prompt(user: CurrentUser, prompt: str = Body(embed=True)):
    """Answer a prompt using the recent history and the conversation summary.

    The question and the answer are saved to the database, and the summary is
    refreshed afterwards if enough old messages have accumulated.

    Args:
        user: The signed-in user.
        prompt: The user's question.

    Returns:
        A dict with the model's reply under the ``answer`` key.
    """
    summary = get_summary(user_id=user.id)
    history = get_user_requests(user_id=user.id, limit=cfg.keep_last)

    response = client.generate(prompt, history, summary.text if summary else None)
    add_request_data(user_id=user.id, prompt=prompt, response=response)

    update_summary(user.id)
    return {"answer": response}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )
