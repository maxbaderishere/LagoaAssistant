from fastapi import FastAPI, Body
from db import Base, engine
from gemini_client import Client
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield
app = FastAPI(lifespan=lifespan)
client = Client()

@app.get("/requests")
def get_requests():
    return "hi"


@app.post("/requests")
def send_prompt(
    prompt: str = Body(embed=True)
):
    answer = client.generate(prompt)
    return {"answer" : answer}