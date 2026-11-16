from fastapi import FastAPI
from app.config import GROQ_API_KEY

app = FastAPI(title="StudyForge")


@app.get("/")
def home():
    return {"message": "Hello, StudyForge"}


@app.get("/health")
def health():
    return {"status": "ok", "groq_key_set": bool(GROQ_API_KEY)}