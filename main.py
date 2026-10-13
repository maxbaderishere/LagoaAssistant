from fastapi import FastAPI

app = FastAPI()


@app.get("/requests")
def get_requests():
    return "hi"




