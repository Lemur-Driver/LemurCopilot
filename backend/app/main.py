from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import client
from app.routes import students
from app.routes.rag import router as rag_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(rag_router)

@app.get("/")
def root():
    return {"message": "Hola desde FastAPI"}


@app.get("/health")
def health():
    return {"status": "ok"}