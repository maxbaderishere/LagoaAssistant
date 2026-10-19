# Lagoa

[Русский](README.md) | **English**

A personal AI assistant with a web chat. My first pet project.

You ask a question in the web chat, the backend sends it to an AI model together with the context of your previous conversation, saves the question and the answer to a database and returns the answer. Every user has their own account and history: Lagoa remembers what you talked about before, and the next time you sign in, the whole history is loaded from the database.

Lagoa can work with different AI providers: **Groq** (the default) and **Google Gemini** are supported right now.

## Features

- Chat with an AI model through a web interface
- **Multiple AI providers:** Groq and Gemini behind a common interface, switched with one line
- **Conversation memory:** Lagoa remembers the context of previous messages
- Request history stored in SQLite
- **Accounts:** sign-up and sign-in with a login and password, each user has their own history
- Answers are rendered with formatting (lists, bold text, code blocks)
- Responsive interface for desktop and mobile
- Interface in Russian and English with a language switcher

## How Lagoa remembers context

Language models keep no memory between requests, so the context is sent along with every question. To keep requests from growing forever, the history is split into two parts:

- **the most recent messages** (10 by default) are sent to the model word for word;
- **older messages** are compressed into a short summary: key facts about the user, their tasks and agreements. The summary is stored in the database, passed to the model as a system instruction and updated in batches as more old messages pile up.

This way the assistant remembers both the fresh details and the big picture, while requests stay small. The number of verbatim messages and the summary batch size are set in `config.py` (`keep_last` and `summarise_every`).

## Tech stack

- **Python 3.14**
- **FastAPI** — REST API
- **Uvicorn** — ASGI server
- **SQLAlchemy 2** — ORM, SQLite database
- **groq** — Groq API client
- **google-genai** — Gemini API client
- **pwdlib (Argon2)** — password hashing
- **PyJWT** — access tokens
- **python-dotenv** — loads keys and secrets from `.env`
- **HTML / CSS / JavaScript** — frontend without frameworks
- **uv** — dependency management

## Project structure

```
├── main.py               # FastAPI app and endpoints
├── auth.py               # sign-up, sign-in and the get_current_user dependency
├── security.py           # password hashing and JWT tokens
├── schemas.py            # Pydantic request and response schemas
├── db.py                 # database models and helper functions
├── config.py             # settings and API keys from .env
├── ai/
│   ├── client.py         # abstract AI client class
│   ├── gemini_client.py  # Gemini client implementation
│   └── groq_client.py    # Groq client implementation
├── frontend/
│   ├── index.html        # chat page
│   ├── login.html        # sign-in and sign-up page
│   ├── styles.css        # styles
│   ├── i18n.js           # interface translations (RU / EN)
│   ├── api.js            # API address, token storage and authorized requests
│   ├── auth.js           # sign-in and sign-up logic
│   └── app.js            # chat logic
└── pyproject.toml        # dependencies
```

## AI providers

AI clients inherit from the abstract `Client` class. To plug in another model, you only need to write a new class with a `generate` method; the rest of the code works with any client the same way.

The provider is chosen with one line in `main.py`:

```python
client: Client = GroqClient(api_key=cfg.groq_api_key)        # Groq (default)
# client: Client = GeminiClient(api_key=cfg.gemini_api_key)  # Gemini
```

A specific model can be passed with the `model` parameter, e.g. `GroqClient(api_key=..., model="...")`. See the model lists in the [Groq](https://console.groq.com/docs/models) and [Gemini](https://ai.google.dev/gemini-api/docs/models) docs.

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
uv run uvicorn main:app --reload
```

The API will be available at http://localhost:8000, interactive docs at http://localhost:8000/docs.

### 5. Run the frontend

The frontend must be served on port 5500 (this origin is allowed in the CORS settings). Serve only the `frontend/` folder, for example:

```bash
python -m http.server 5500 -d frontend
```

Then open http://localhost:5500/index.html. With Live Server in VS Code, open `frontend/index.html`. If you're not signed in, the chat redirects to the sign-in and sign-up page.

## API

| Method | Path             | Description                                          |
|--------|------------------|------------------------------------------------------|
| POST   | `/auth/register` | Sign up; returns an access token                     |
| POST   | `/auth/login`    | Sign in; returns an access token                     |
| GET    | `/auth/me`       | The signed-in user                                   |
| GET    | `/requests`      | Full request history of the signed-in user           |
| POST   | `/requests`      | Send a question to the AI, with conversation context |

All endpoints except sign-up and sign-in require an `Authorization: Bearer <token>` header.

Example request:

```bash
curl -X POST http://localhost:8000/requests \
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
- Each user has a single shared conversation; separate chats are not supported yet.
- The summary of older messages loses small details: the model remembers the gist, not the exact wording.
- The model is chosen in code, not in the interface.

## Roadmap

- [x] Send the conversation history to the model so the assistant keeps context
- [x] Support multiple AI providers (Groq and Gemini)
- [x] Add sign-up and authentication
- [ ] Pick the model right in the interface
- [ ] Multiple separate chats per user
- [ ] Add more interface languages
- [ ] Write tests
