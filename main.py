"""FastAPI application for Lagoa, a personal AI assistant.

Exposes the chat endpoints, keeps the conversation history in the database
and maintains a running summary of older messages so the model keeps context.
"""

from fastapi import FastAPI, Body, Request
from db import Base, add_request_data, engine, get_summary, get_unsummarized_requests, get_user_requests, save_summary
from ai import Client, GeminiClient, GroqClient
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

#client: Client = GeminiClient(api_key=cfg.gemini_api_key)
client: Client = GroqClient(api_key=cfg.groq_api_key)


def update_summary(ip: str) -> None:
    """Fold old messages of a user into their conversation summary.

    The last ``cfg.keep_last`` messages are always left out, because they are
    sent to the model verbatim. The summary is only updated once at least
    ``cfg.summarise_every`` older messages have piled up, so the extra model
    call doesn't happen on every request.

    Args:
        ip: IP address that identifies the user.
    """
    summary = get_summary(ip_adress=ip)
    old_text = summary.text if summary else ""
    last_id = summary.last_summarized_id if summary else 0

    new_messages = get_unsummarized_requests(ip_adress=ip, after_id=last_id)
    to_summarise = new_messages[:-cfg.keep_last]
    if len(to_summarise) < cfg.summarise_every:
        return

    new_text = client.summarise(old_text, to_summarise)
    save_summary(ip_adress=ip, text=new_text, last_summarized_id=to_summarise[-1].id)

@app.get("/requests")
def get_requests(request: Request):
    """Return the full chat history of the current user, oldest first."""
    user_ip_adress = request.client.host
    user_requests = get_user_requests(ip_adress=user_ip_adress)
    return user_requests


@app.post("/requests")
def send_prompt(request: Request, prompt: str = Body(embed=True)):
    """Answer a prompt using the recent history and the conversation summary.

    The question and the answer are saved to the database, and the summary is
    refreshed afterwards if enough old messages have accumulated.

    Args:
        request: Incoming request, used to get the user's IP address.
        prompt: The user's question.

    Returns:
        A dict with the model's reply under the ``answer`` key.
    """
    ip = request.client.host
    summary = get_summary(ip_adress=ip)
    history = get_user_requests(ip_adress=ip, limit=cfg.keep_last)

    response = client.generate(prompt, history, summary.text if summary else None)
    add_request_data(ip_adress=ip, prompt=prompt, response=response)

    update_summary(ip)
    return {"answer": response}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )
