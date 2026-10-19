# Lagoa

[Русский](README.md) | **English**

A personal AI assistant powered by Google Gemini. My first pet project.

You ask a question in the web chat, the backend sends it to Gemini together with the context of your previous conversation, saves the question and the answer to a database and returns the answer. Lagoa remembers what you talked about before, and the next time you open the chat, the whole history is loaded from the database.

## Features

- Chat with Gemini through a web interface
- **Conversation memory:** Lagoa remembers the context of previous messages
- Request history stored in SQLite
- History is tied to the user's IP address
- Answers are rendered with formatting (lists, bold text, code blocks)
- Responsive interface for desktop and mobile

## How Lagoa remembers context

Language models keep no memory between requests, so the context is sent along with every question. To keep requests from growing forever, the history is split into two parts:

- **the most recent messages** (10 by default) are sent to Gemini word for word;
- **older messages** are compressed into a short summary: key facts about the user, their tasks and agreements. The summary is stored in the database, passed to the model as a system instruction and updated in batches as more old messages pile up.

This way the assistant remembers both the fresh details and the big picture, while requests stay small. The number of verbatim messages and the summary batch size are set in `config.py` (`keep_last` and `summarise_every`).

## Tech stack

- **Python 3.14**
- **FastAPI** — REST API
- **Uvicorn** — ASGI server
- **SQLAlchemy 2** — ORM, SQLite database
- **google-genai** — Gemini API client
- **python-dotenv** — loads the API key from `.env`
- **HTML / CSS / JavaScript** — single-file frontend, no frameworks
- **uv** — dependency management

## Project structure

```
├── main.py               # FastAPI app and endpoints
├── db.py                 # database models and helper functions
├── config.py             # settings and the API key from .env
├── ai/
│   ├── client.py         # abstract AI client class
│   └── gemini_client.py  # Gemini client implementation
├── index.html            # frontend (chat)
└── pyproject.toml        # dependencies
```

AI clients inherit from the abstract `Client` class. To plug in another model, you only need to write a new class with a `generate` method; the rest of the code works with any client the same way.

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

### 3. Add your Gemini API key

You can get a key in [Google AI Studio](https://aistudio.google.com/apikey). Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key
```

### 4. Run the backend

```bash
uv run uvicorn main:app --reload
```

The API will be available at http://localhost:8000, interactive docs at http://localhost:8000/docs.

### 5. Run the frontend

The frontend must be served on port 5500 (this origin is allowed in the CORS settings). For example, with Live Server in VS Code, or:

```bash
python -m http.server 5500
```

Then open http://localhost:5500/index.html.

## API

| Method | Path        | Description                                        |
|--------|-------------|----------------------------------------------------|
| GET    | `/requests` | Full request history of the current user (by IP)   |
| POST   | `/requests` | Send a question to the AI, with conversation context |

Example request:

```bash
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hi! Who are you?"}'
```

Response:

```json
{"answer": "Hi! I'm a large language model..."}
```

## Limitations

- Users are identified only by IP address; there is no authentication.
- Each user has a single shared conversation; separate chats are not supported yet.
- The summary of older messages loses small details: the model remembers the gist, not the exact wording.

## Roadmap

- [x] Send the conversation history to Gemini so the assistant keeps context
- [ ] Model switching: support other AI models and pick the model right in the interface
- [ ] Multiple separate chats per user
- [ ] Add sign-up and authentication
- [ ] Write tests
