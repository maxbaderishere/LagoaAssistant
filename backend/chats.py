"""Chat endpoints: list, create, rename and delete chats, read and send messages."""

import logging
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.ai import Client, UnknownModelError
from backend.ai.setup import quick_reply_client, registry, title_client
from backend.auth import CurrentUser
from backend.config import cfg
from backend.db import (
    Chat, add_message, create_chat, delete_chat, get_chat_messages, get_summary,
    get_unsummarized_messages, get_user_chat, get_user_chats, rename_chat, save_summary,
)
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


def update_summary(chat_id: int, client: Client) -> None:
    """Fold old messages of a chat into its conversation summary.

    The last ``cfg.keep_last`` messages are always left out, because they are
    sent to the model verbatim. The summary is only updated once at least
    ``cfg.summarise_every`` older messages have piled up, so the extra model
    call doesn't happen on every request.

    Args:
        chat_id: Id of the chat whose summary to update.
        client: Client of the model that writes the summary.
    """
    summary = get_summary(chat_id=chat_id)
    old_text = summary.text if summary else ""
    last_id = summary.last_summarized_id if summary else 0

    new_messages = get_unsummarized_messages(chat_id=chat_id, after_id=last_id)
    to_summarise = new_messages[:-cfg.keep_last]
    if len(to_summarise) < cfg.summarise_every:
        return

    new_text = client.summarise(old_text, to_summarise)
    save_summary(chat_id=chat_id, text=new_text, last_summarized_id=to_summarise[-1].id)


def name_chat(chat: Chat, client: Client, prompt: str, answer: str) -> Chat:
    """Rename a chat with a title made up by the model; keep the old title on failure."""
    try:
        title = client.make_title(prompt, answer)
    except Exception:
        logger.exception("Couldn't generate a title for chat %s", chat.id)
        return chat
    return rename_chat(chat_id=chat.id, title=title) if title else chat


def suggest_replies(answer: str) -> list[str]:
    """Quick replies from the small helper model; none if it's unavailable or fails."""
    if quick_reply_client is None:
        return []
    try:
        return quick_reply_client.suggest_replies(answer)
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


@router.post("/{chat_id}/messages")
def send_message(chat: OwnedChat, data: PromptRequest) -> AnswerResponse:
    """Answer a prompt using the chat's recent messages and its summary.

    The question and the answer are saved to the chat, and the summary is
    refreshed afterwards if enough old messages have accumulated.

    Raises:
        HTTPException: 400 if the requested model is not available.
    """
    model_id = data.model or registry.default_id
    try:
        client = registry.get(model_id)
    except UnknownModelError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown model: {model_id}")

    summary = get_summary(chat_id=chat.id)
    history = get_chat_messages(chat_id=chat.id, limit=cfg.keep_last)

    answer = client.generate(data.prompt, history, summary.text if summary else None)
    updated_chat = add_message(chat_id=chat.id, prompt=data.prompt, response=answer)

    # A new chat gets a title from the small title model if there is one,
    # otherwise from the chat's model. add_message has already named it
    # after the prompt, which stays as a fallback if the model call fails.
    if chat.title is None:
        updated_chat = name_chat(updated_chat, title_client or client, data.prompt, answer)

    update_summary(chat.id, client)
    return AnswerResponse(answer=answer, model=model_id, chat=ChatOut.model_validate(updated_chat))


@router.get("/{chat_id}/suggestions")
def suggestions(chat: OwnedChat) -> SuggestionsResponse:
    """Suggest quick replies to the chat's last answer.

    Separate from sending a message so the answer is shown right away and
    the buttons appear a moment later.
    """
    last = get_chat_messages(chat_id=chat.id, limit=1)
    return SuggestionsResponse(suggestions=suggest_replies(last[0].response) if last else [])
