from fastapi import FastAPI

app = FastAPI(title="MediaCompass API")


@app.get("/")
def read_root():
    return {"message": "MediaCompass API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}