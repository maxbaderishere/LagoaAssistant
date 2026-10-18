from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine, get_user_requests, add_request_data
from gemini_client import Client
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    print("All tabels created!")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Lagoa"
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)
client = Client()

@app.get("/requests")
def get_requests(request: Request):
    user_ip_adress = request.client.host
    print(user_ip_adress) 
    user_requests = get_user_requests(ip_adress=user_ip_adress)
    return user_requests


@app.post("/requests")
def send_prompt(
    request: Request,
    prompt: str = Body(embed=True)
):
    user_ip_adress = request.client.host
    answer = client.generate(prompt)
    add_request_data(
        ip_adress=user_ip_adress,
        prompt=prompt,
        response=answer,
    )
    return {"answer" : answer}