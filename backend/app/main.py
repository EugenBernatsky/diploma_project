from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.db.mongo import connect_to_mongo, close_mongo_connection, get_db
from app.db.indexes import create_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await create_indexes()
    yield
    await close_mongo_connection()


app = FastAPI(title="MediaCompass API", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "MediaCompass API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
async def health_db():
    db = get_db()
    ping = await db.command("ping")
    return {"status": "ok", "db": ping}