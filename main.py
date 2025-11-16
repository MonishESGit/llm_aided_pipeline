# main.py
from fastapi import FastAPI
from service import api_v1, api_v2

app = FastAPI(title="Time Series Preprocessing Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_v1.router)
app.include_router(api_v2.router)
