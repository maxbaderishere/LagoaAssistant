"""Chat endpoints: list, create, rename and delete chats, read and send messages."""

import asyncio
import logging
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from starlette.concurrency import run_in_threadpool

from backend.ai import Client, UnknownModelError
from backend.ai.setup import helper_client, registry
from backend.auth import CurrentUser
from backend.config import cfg
from backend.db import (
    Chat, add_message, create_chat, delete_chat, get_chat_messages, get_summary,
    get_unsummarized_messages, get_user_chat, get_user_chats, rename_chat, save_summary,
)
from backend.helpers import ReplySuggester, Summariser, TitleWriter
from backend.schemas import AnswerResponse, ChatOut, ChatRename, MessageOut, PromptRequest, SuggestionsResponse

router = APIRouter(prefix="/chats", tags=["chats"])
logger = logging.getLogger(__name__)


def get_owned_chat(chat_id: int, user: CurrentUser) -> Chat:
    """Return the chat from the URL if it belongs to the signed-in user.

    Raises:
        HTTPException: 404 if there is no such chat or it belongs to someone
            else, so other users' chat ids aren't revealed.
    """
    chat = get_user_chat(user_id=user.id, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


OwnedChat: TypeAlias = Annotated[Chat, Depends(get_owned_chat)]


def update_summary(chat_id: int, client: Client | None) -> None:
    """Fold old messages of a chat into its conversation summary.

    The last ``cfg.keep_last`` messages are always left out, because they are
    sent to the model verbatim. The summary is only updated once at least
    ``cfg.summarise_every`` older messages have piled up, so the extra model
    call doesn't happen on every request.

    Args:
        chat_id: Id of the chat whose summary to update.
        client: Client of the model that writes the summary (the ``summary``
            helper role, see ``cfg.helper_models``), or None to skip it.
    """
    if client is None:
        return
    summary = get_summary(chat_id=chat_id)
    old_text = summary.text if summary else ""
    last_id = summary.last_summarized_id if summary else 0

    new_messages = get_unsummarized_messages(chat_id=chat_id, after_id=last_id)
    to_summarise = new_messages[:-cfg.keep_last]
    if len(to_summarise) < cfg.summarise_every:
        return

    new_text = Summariser(client).summarise(old_text, to_summarise)
    save_summary(chat_id=chat_id, text=new_text, last_summarized_id=to_summarise[-1].id)


def name_chat(chat: Chat, client: Client | None, prompt: str, answer: str) -> Chat:
    """Rename a chat with a title made up by the model; keep the old title on failure or without a model."""
    if client is None:
        return chat
    try:
        title = TitleWriter(client).write(prompt, answer)
    except Exception:
        logger.exception("Couldn't generate a title for chat %s", chat.id)
        return chat
    return rename_chat(chat_id=chat.id, title=title) if title else chat


def suggest_replies(answer: str) -> list[str]:
    """Quick replies from the ``quick_replies`` helper model; none if it's unavailable or fails."""
    try:
        client = helper_client("quick_replies", chat_client=registry.get())
    except UnknownModelError:
        return []
    if client is None:
        return []
    try:
        return ReplySuggester(client).suggest(answer)
    except Exception:
        logger.exception("Couldn't suggest quick replies")
        return []


@router.get("")
def list_chats(user: CurrentUser) -> list[ChatOut]:
    """Return the user's chats, most recently active first."""
    return [ChatOut.model_validate(chat) for chat in get_user_chats(user_id=user.id)]


@router.post("", status_code=status.HTTP_201_CREATED)
def new_chat(user: CurrentUser) -> ChatOut:
    """Create an empty chat. It gets a title from its first message."""
    return ChatOut.model_validate(create_chat(user_id=user.id))


@router.patch("/{chat_id}")
def rename(chat: OwnedChat, data: ChatRename) -> ChatOut:
    """Rename a chat."""
    return ChatOut.model_validate(rename_chat(chat_id=chat.id, title=data.title))


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(chat: OwnedChat) -> Response:
    """Delete a chat with all its messages."""
    delete_chat(chat_id=chat.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{chat_id}/messages")
def list_messages(chat: OwnedChat) -> list[MessageOut]:
    """Return all messages of a chat, oldest first."""
    return [MessageOut.model_validate(m) for m in get_chat_messages(chat_id=chat.id)]


# Not a real HTTP status, but a common convention (from nginx) for "the client
# closed the request"; nobody receives it, it only shows up in the server log.
CLIENT_CLOSED_REQUEST = 499


async def wait_for_disconnect(request: Request) -> None:
    """Return once the client closes the connection, e.g. presses the stop button.

    Waiting the whole time is what makes this reliable: after the request body
    is read, the server only notices a closed connection while it's listening.
    """
    while (await request.receive())["type"] != "http.disconnect":
        pass


@router.post("/{chat_id}/messages")
async def send_message(request: Request, chat: OwnedChat, data: PromptRequest) -> AnswerResponse:
    """Answer a prompt using the chat's recent messages and its summary.

    The question and the answer are saved to the chat, and the summary is
    refreshed afterwards if enough old messages have accumulated. If the user
    cancels the request while the model is answering, nothing is saved.

    The endpoint is async only to notice the cancellation; the blocking model
    and database calls run in a thread pool.

    Raises:
        HTTPException: 400 if the requested model is not available.
    """
    model_id = data.model or registry.default_id
    try:
        client = registry.get(model_id)
    except UnknownModelError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown model: {model_id}")

    summary = await run_in_threadpool(get_summary, chat_id=chat.id)
    history = await run_in_threadpool(get_chat_messages, chat_id=chat.id, limit=cfg.keep_last)

    disconnected = asyncio.create_task(wait_for_disconnect(request))
    try:
        answer = await run_in_threadpool(client.generate, data.prompt, history, summary.text if summary else None)
    finally:
        cancelled = disconnected.done()
        disconnected.cancel()

    # The model can't be interrupted mid-answer, but a cancelled answer isn't saved.
    if cancelled:
        logger.info("Request for chat %s was cancelled; the answer is not saved", chat.id)
        return Response(status_code=CLIENT_CLOSED_REQUEST)

    updated_chat = await run_in_threadpool(add_message, chat_id=chat.id, prompt=data.prompt, response=answer)

    # A new chat gets a title from the small title model if there is one,
    # otherwise from the chat's model. add_message has already named it
    # after the prompt, which stays as a fallback if the model call fails.
    if chat.title is None:
        updated_chat = await run_in_threadpool(name_chat, updated_chat, helper_client("title", client), data.prompt, answer)

    await run_in_threadpool(update_summary, chat.id, helper_client("summary", client))
    return AnswerResponse(answer=answer, model=model_id, chat=ChatOut.model_validate(updated_chat))


@router.get("/{chat_id}/suggestions")
def suggestions(chat: OwnedChat) -> SuggestionsResponse:
    """Suggest quick replies to the chat's last answer.

    Separate from sending a message so the answer is shown right away and
    the buttons appear a moment later.
    """
    last = get_chat_messages(chat_id=chat.id, limit=1)
    return SuggestionsResponse(suggestions=suggest_replies(last[0].response) if last else [])
