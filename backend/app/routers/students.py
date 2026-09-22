from fastapi import APIRouter

from app.database import client


router = APIRouter(
    prefix="/students",
    tags=["students"],
)


@router.get("/mongo-test")
async def mongo_test():
    await client.admin.command("ping")

    return {"mongodb": "connected"}