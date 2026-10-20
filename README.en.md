# Lagoa

[Português](README.md) | **English** | [Русский](README.ru.md)

An open-source chat for working with AI models, built for the Brazilian market.

## About the project

Lagoa brings different AI models — cloud and local — into one interface in Brazilian Portuguese. It remembers your conversations and lets you pick the model that fits each task.

- **Portuguese first:** the interface and texts are made for Brazilian Portuguese, and models are chosen and evaluated by how well they handle it.
- **Free and open:** open source, free models wherever possible, and local models via Ollama that work without internet and keep your data on your computer.
- **Easy to self-host:** anyone can run their own Lagoa.

You ask a question in the web chat, the backend sends it to an AI model together with the context of your previous conversation, saves the question and the answer to a database and returns the answer. Every user has their own account and as many chats as they like: in each one Lagoa remembers what you talked about before, and the next time you sign in, all chats are loaded from the database.

Lagoa currently works with **Groq** (the default), **Google Gemini** and local models via **Ollama**. There is also a client for Anthropic's **Claude**: it's paid and, for now, serves as the judge in the Portuguese tests rather than as a chat model.

## Features

- Chat with an AI model through a web interface
- **Multiple AI providers:** Groq, Gemini and local models via Ollama, with the model picked below the message box
- **Works offline:** with Ollama, Lagoa answers with a local model on your computer
- **Quick replies:** when the assistant asks a question, reply buttons appear under the answer
- **Stop button:** while the model is answering, the request can be cancelled and the question goes back into the input
- **Conversation memory:** Lagoa remembers the context of previous messages
- Request history stored in PostgreSQL
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

This way the assistant remembers both the fresh details and the big picture, while requests stay small. The number of verbatim messages and the summary batch size are set in `backend/config.py` (`keep_last` and `summarise_every`). The summary is written by the `summary` role in `helper_models` (see [AI providers](#ai-providers)); by default, the chat's own model.

## Tech stack

- **Python 3.14**
- **FastAPI** — REST API
- **Uvicorn** — ASGI server
- **SQLAlchemy 2** — ORM
- **PostgreSQL** + **psycopg** — database
- **Alembic** — database migrations
- **groq** — Groq API client
- **google-genai** — Gemini API client
- **Ollama** + **httpx** — local models without internet
- **pwdlib (Argon2)** — password hashing
- **PyJWT** — access tokens
- **anthropic** — Claude API client
- **python-dotenv** — loads keys and secrets from `.env`
- **PyYAML** — tasks for the Portuguese tests (the `evals` dependency group)
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
│   ├── helpers/              # helper tasks: chat titles, quick replies, summaries
│   └── ai/
│       ├── claude_client.py  # Claude (Anthropic) client
│       ├── client.py         # abstract AI client class
│       ├── context.py        # conversation context, built once for every provider
│       ├── gemini_client.py  # Gemini client implementation
│       ├── groq_client.py    # Groq client implementation
│       ├── ollama_client.py  # client for local Ollama models
│       ├── registry.py       # registry of available models
│       └── setup.py          # builds the registry from config.py
├── evals/                    # Portuguese tests for models (in progress)
│   ├── tasks/pt_br.yaml      # tasks with grading criteria
│   ├── tester.py             # PortugueseTester: model under test + judge model
│   ├── judge.py              # Judge and ClaudeJudge
│   ├── checks.py             # automatic checks, no judge needed
│   └── report.py             # scores and model leaderboard
├── frontend/
│   ├── index.html            # chat page
│   ├── login.html            # sign-in and sign-up page
│   ├── styles.css            # styles
│   ├── i18n.js               # interface translations (RU / EN / PT / ES)
│   ├── greetings.js          # welcome screen phrases for each language and time of day
│   ├── api.js                # API address, token storage and authorized requests
│   ├── auth.js               # sign-in and sign-up logic
│   └── app.js                # chat logic
├── migrations/               # Alembic database migrations
├── .env                      # API keys and secrets (not in Git)
├── alembic.ini               # Alembic settings
└── pyproject.toml            # dependencies
```

## AI providers

AI clients inherit from the abstract `Client` class. Its `generate(prompt, history, summary)` method is shared: it builds a provider-neutral `Context` (`backend/ai/context.py`) with the system instruction and the messages. To plug in a new provider, you only need to write a class with a `_complete(context)` method that translates this context into the provider's API format; the rest of the code works with any client the same way.

The available providers are `groq`, `gemini`, `ollama` and `claude`. Claude is paid and needs `ANTHROPIC_API_KEY`; to use it in the chat, add it to `chat_models`.

The available models are listed in `backend/config.py`:

```python
chat_models = [
    {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B"},
    {"provider": "gemini", "model": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
    {"provider": "ollama", "model": "qwen3.5:4b", "name": "Qwen 3.5 4B"},
]
default_model = "qwen/qwen3.8-27b"
helper_models = {
    "title": {"provider": "ollama", "model": "qwen3.5:4b", "fallback": "chat"},
    "quick_replies": {"provider": "ollama", "model": "qwen3.5:4b", "fallback": None},
    "summary": None,
}
```

On startup, `ModelRegistry` (`backend/ai/registry.py`) creates a client for every available model: a cloud model if its provider's API key is set, a local one if Ollama is running and the model is pulled. Users pick a model below the message box, and the choice is remembered in the browser. To add another model from the same provider, add a line to `chat_models`. See the model names in the [Groq](https://console.groq.com/docs/models) and [Gemini](https://ai.google.dev/gemini-api/docs/models) docs and the [Ollama library](https://ollama.com/library).

Models have two roles:

- **`chat_models`** — the models users chat with and pick in the interface;
- **`helper_models`** — models that work for the app rather than talk to users: `title` names new chats, `quick_replies` suggests reply buttons and `summary` compresses older messages into the chat's memory.

A role set to `None` is done by the chat's own model. If a helper model isn't available, `fallback` decides: `"chat"` hands the work to the chat's model and `None` skips the task. Quick replies use `None` so they never spend the cloud models' limits. The tasks themselves live in `backend/helpers/` and work with any model.

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
ANTHROPIC_API_KEY=your_anthropic_key
JWT_SECRET=a_long_random_string
```

You can generate a secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Get a Groq key in the [Groq console](https://console.groq.com/keys), a Gemini key in [Google AI Studio](https://aistudio.google.com/apikey), and a Claude key (optional, paid) in the [Anthropic Console](https://console.anthropic.com/).

### 4. Set up the database

Lagoa uses PostgreSQL. Install [PostgreSQL](https://www.postgresql.org/download/) and create a user and a database (change the password):

```bash
psql -U postgres -c "CREATE ROLE lagoa LOGIN PASSWORD 'change_this_password'" -c "CREATE DATABASE lagoa OWNER lagoa"
```

Then add the database address to `.env`:

```
DATABASE_URL=postgresql+psycopg://lagoa:change_this_password@localhost:5432/lagoa
```

Tables are created and updated automatically: on startup the backend applies any pending Alembic migrations (the `migrations/` folder).

**Changed the models in `backend/db.py`?** Generate a migration, read the new file in `migrations/versions/` and apply it:

```bash
uv run alembic revision --autogenerate -m "Describe the change"
uv run alembic upgrade head
```

### 5. Run the backend

```bash
uv run uvicorn backend.main:app --reload
```

The API will be available at http://localhost:8000, interactive docs at http://localhost:8000/docs.

### 6. Run the frontend

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
{
  "answer": "Hi! I'm Lagoa, an AI assistant...",
  "model": "qwen/qwen3.8-27b",
  "chat": {"id": 1, "title": "Meeting Lagoa", "created_at": "2026-10-19T12:00:00Z", "updated_at": "2026-10-19T12:00:05Z"}
}
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
- [ ] Tests that score from 0 to 100 how well each model handles Portuguese (in progress: the `evals/` skeleton and 38 draft tasks)
- [ ] More free models with good Portuguese
- [ ] Personalization: the user's conversation style that every model follows
- [ ] Chat commands such as `/context`
- [ ] Write tests
