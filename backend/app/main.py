from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import client, ensure_indexes
from app.routes import students
from app.routes.rag import router as rag_router
from app.routes.lessons import router as lessons_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.admin.command("ping")
    await ensure_indexes()
    yield
    await client.close()
 
 
app = FastAPI(lifespan=lifespan)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(students.router)
app.include_router(rag_router)
app.include_router(lessons_router)

 
@app.get("/")
def root():
    return {"message": "Hola desde FastAPI"}
 
 
@app.get("/health")
def health():
    return {"status": "ok"}