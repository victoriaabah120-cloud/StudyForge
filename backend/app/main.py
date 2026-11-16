from fastapi import FastAPI

app = FastAPI(title="StudyForge")

@app.get("/")
def home():
    return {"message": "Hello, StudyForge"}

@app.get("/health")
def health():
    return {"status": "ok"}