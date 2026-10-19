# Lagoa

[Português](README.md) | **English** | [Русский](README.ru.md)

An open-source chat for working with AI models, built for the Brazilian market.

## About the project

Lagoa brings different AI models — cloud and local — into one interface in Brazilian Portuguese. It remembers your conversations and lets you pick the model that fits each task.

- **Portuguese first:** the interface and texts are made for Brazilian Portuguese, and models are chosen and evaluated by how well they handle it.
- **Free and open:** open source, free models wherever possible, and local models via Ollama that work without internet and keep your data on your computer.
- **Easy to self-host:** anyone can run their own Lagoa.

You ask a question in the web chat, the backend sends it to an AI model together with the context of your previous conversation, saves the question and the answer to a database and returns the answer. Every user has their own account and as many chats as they like: in each one Lagoa remembers what you talked about before, and the next time you sign in, all chats are loaded from the database.

Lagoa currently works with **Groq** (the default), **Google Gemini** and local models via **Ollama**.

## Features

- Chat with an AI model through a web interface
- **Multiple AI providers:** Groq, Gemini and local models via Ollama, with the model picked below the message box
- **Works offline:** with Ollama, Lagoa answers with a local model on your computer
- **Quick replies:** when the assistant asks a question, reply buttons appear under the answer
- **Stop button:** while the model is answering, the request can be cancelled and the question goes back into the input
- **Conversation memory:** Lagoa remembers the context of previous messages
- Request history stored in SQLite
- **Accounts:** sign-up and sign-in with a login and password
- **Multiple chats:** create, rename and delete chats; chats are grouped by date, each with its own history and memory
- **Lively welcome screen:** the greeting, subtitle and input hints change with the time of day
- Answers are rendered with formatting (lists, bold text, code blocks)
- Responsive interface for desktop and mobile
- Interface in Russian, English, Portuguese and Spanish with a language menu

## How Lagoa remembers context

Language models keep no memory between requests, so the context is sent along with every question. To keep requests from growing forever, the history is split into two parts:

- **the most recent messages** (10 by default) are sent to the model word for word;
- **older messages** are compressed into a short summary: key facts about the user, their tasks and agreements. The summary is stored in the database, passed to the model as a system instruction and updated in batches as more old messages pile up.

This way the assistant remembers both the fresh details and the big picture, while requests stay small. The number of verbatim messages and the summary batch size are set in `backend/config.py` (`keep_last` and `summarise_every`).

## Tech stack

- **Python 3.14**
- **FastAPI** — REST API
- **Uvicorn** — ASGI server
- **SQLAlchemy 2** — ORM, SQLite database
- **groq** — Groq API client
- **google-genai** — Gemini API client
- **Ollama** + **httpx** — local models without internet
- **pwdlib (Argon2)** — password hashing
- **PyJWT** — access tokens
- **python-dotenv** — loads keys and secrets from `.env`
- **HTML / CSS / JavaScript** — frontend without frameworks
- **uv** — dependency management

## Project structure

```
├── backend/
│   ├── main.py               # FastAPI app, wires all endpoints together
│   ├── auth.py               # sign-up, sign-in and the get_current_user dependency
│   ├── chats.py              # chat and message endpoints
│   ├── security.py           # password hashing and JWT tokens
│   ├── schemas.py            # Pydantic request and response schemas
│   ├── db.py                 # database models and helper functions
│   ├── config.py             # settings and API keys from .env
│   └── ai/
│       ├── client.py         # abstract AI client class
│       ├── gemini_client.py  # Gemini client implementation
│       ├── groq_client.py    # Groq client implementation
│       ├── ollama_client.py  # client for local Ollama models
│       ├── registry.py       # registry of available models
│       └── setup.py          # builds the registry from config.py
├── frontend/
│   ├── index.html            # chat page
│   ├── login.html            # sign-in and sign-up page
│   ├── styles.css            # styles
│   ├── i18n.js               # interface translations (RU / EN / PT / ES)
│   ├── greetings.js          # welcome screen phrases for each language and time of day
│   ├── api.js                # API address, token storage and authorized requests
│   ├── auth.js               # sign-in and sign-up logic
│   └── app.js                # chat logic
├── .env                      # API keys and secrets (not in Git)
├── data.db                   # SQLite database (created automatically, not in Git)
└── pyproject.toml            # dependencies
```

## AI providers

AI clients inherit from the abstract `Client` class. To plug in a new provider, you only need to write a class with a `generate` method; the rest of the code works with any client the same way.

The available models are listed in `backend/config.py`:

```python
models = [
    {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B"},
    {"provider": "gemini", "model": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
    {"provider": "ollama", "model": "qwen3.5:4b", "name": "Qwen 3.5 4B"},
]
default_model = "qwen/qwen3.8-27b"
title_model = {"provider": "ollama", "model": "qwen3.5:4b"}
quick_reply_model = {"provider": "ollama", "model": "qwen3.5:4b"}
```

On startup, `ModelRegistry` (`backend/ai/registry.py`) creates a client for every available model: a cloud model if its provider's API key is set, a local one if Ollama is running and the model is pulled. Users pick a model below the message box, and the choice is remembered in the browser. To add another model from the same provider, add a line to `models`. See the model names in the [Groq](https://console.groq.com/docs/models) and [Gemini](https://ai.google.dev/gemini-api/docs/models) docs and the [Ollama library](https://ollama.com/library).

`title_model` is a separate helper model that names new chats, so naming doesn't use up the main models' limits. If it isn't available, the chat's own model names the chat.

`quick_reply_model` is a local model that suggests quick replies. Cloud models aren't used for this: without a local model, no buttons are shown.

### Local models (Ollama)

With [Ollama](https://ollama.com/download), Lagoa works without internet. Install Ollama and pull a model:

```bash
ollama pull qwen3.5:4b
```

Then restart the backend: pulled models are checked on startup. The Ollama server defaults to `http://localhost:11434`; change it with `OLLAMA_URL` in `.env`. A local model runs on your own computer, so without a GPU long answers can take a minute or two.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/maxbaderishere/LagoaAssistant.git
cd LagoaAssistant
```

### 2. Install dependencies

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

### 3. Add your API keys and token secret

Create a `.env` file in the project root. You only need the key for the AI provider you use, but `JWT_SECRET` is required: it signs the sign-in tokens.

```
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
JWT_SECRET=a_long_random_string
```

You can generate a secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Get a Groq key in the [Groq console](https://console.groq.com/keys) and a Gemini key in [Google AI Studio](https://aistudio.google.com/apikey).

### 4. Run the backend

```bash
uv run uvicorn backend.main:app --reload
```

The API will be available at http://localhost:8000, interactive docs at http://localhost:8000/docs.

### 5. Run the frontend

The frontend must be served on port 5500 (this origin is allowed in the CORS settings). Serve only the `frontend/` folder, for example:

```bash
python -m http.server 5500 -d frontend
```

Then open http://localhost:5500/index.html. With Live Server in VS Code, open `frontend/index.html`. If you're not signed in, the chat redirects to the sign-in and sign-up page.

## API

| Method | Path                     | Description                                     |
|--------|--------------------------|-------------------------------------------------|
| POST   | `/auth/register`         | Sign up; returns an access token                |
| POST   | `/auth/login`            | Sign in; returns an access token                |
| GET    | `/auth/me`               | The signed-in user                              |
| GET    | `/chats`                 | The user's chats, most recent first             |
| POST   | `/chats`                 | Create an empty chat                            |
| PATCH  | `/chats/{id}`            | Rename a chat                                   |
| DELETE | `/chats/{id}`            | Delete a chat with all its messages             |
| GET    | `/chats/{id}/messages`   | Messages of a chat                              |
| GET    | `/chats/{id}/suggestions`| Quick replies to the chat's last answer         |
| POST   | `/chats/{id}/messages`   | Send a question to a chat; returns the answer   |
| GET    | `/models`                | Available models and the default one            |

All endpoints except sign-up, sign-in and `/models` require an `Authorization: Bearer <token>` header.

Example request:

```bash
curl -X POST http://localhost:8000/chats/1/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hi! Who are you?"}'
```

Response:

```json
{"answer": "Hi! I'm a large language model..."}
```

## Limitations

- The sign-in token is kept in the browser's `localStorage`: simple, but less protected against XSS than an httpOnly cookie.
- The summary of older messages loses small details: the model remembers the gist, not the exact wording.
- After an answer is stopped, the model still finishes it in the background; it just isn't saved.

## Roadmap

- [x] Send the conversation history to the model so the assistant keeps context
- [x] Support multiple AI providers (Groq, Gemini and Ollama)
- [x] Add sign-up and authentication
- [x] Pick the model right in the interface
- [x] Multiple separate chats per user
- [x] Add more interface languages (Portuguese and Spanish)
- [ ] A clear message in the chat when a model runs out of quota, instead of a connection error
- [ ] Retry a request after an error or after stopping it
- [ ] Tests that score from 0 to 100 how well each model handles Portuguese
- [ ] More free models with good Portuguese
- [ ] Personalization: the user's conversation style that every model follows
- [ ] Chat commands such as `/context`
- [ ] Write tests
