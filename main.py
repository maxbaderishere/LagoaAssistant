from fastapi import FastAPI
from gemini_client import Client


app = FastAPI()
client = Client()

@app.get("/requests")
def get_requests():
    return "hi"




