# Lagoa

[Русский](README.md) | **English**

A personal AI assistant powered by Google Gemini. My first pet project.

You ask a question in the web chat, the backend sends it to Gemini, saves the question and the answer to a database and returns the answer. The next time you open the chat, your request history is loaded from the database.

## Features

- Chat with Gemini through a simple web interface
- Request history stored in SQLite
- History is tied to the user's IP address
- Answers are rendered with formatting (lists, bold text, code blocks)
- Light and dark themes

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
├── main.py            # FastAPI app and endpoints
├── db.py              # database model and helper functions
├── gemini_client.py   # Gemini API wrapper
├── config.py          # loads settings from .env
├── index.html         # frontend (chat)
└── pyproject.toml     # dependencies
```

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

| Method | Path        | Description                                  |
|--------|-------------|----------------------------------------------|
| GET    | `/requests` | Request history of the current user (by IP)  |
| POST   | `/requests` | Send a question to the AI                    |

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

- The AI doesn't remember the conversation: each question is sent to Gemini on its own.
- Users are identified only by IP address; there is no authentication.

## Roadmap

- [ ] Send the conversation history to Gemini so the assistant keeps context
- [ ] Add sign-up and authentication
- [ ] Write tests
