import os

from pymongo import AsyncMongoClient


MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["MONGODB_DATABASE"]

client = AsyncMongoClient(MONGODB_URI)
database = client[DATABASE_NAME]

students_collection = database["students"]
concepts_collection = database["concepts"]
exercises_collection = database["exercises"]
sessions_collection = database["sessions"]
content_chunks_collection = database["manual_chunks"]


async def ensure_indexes() -> None:
    await students_collection.create_index("email", unique=True)
    await exercises_collection.create_index([("concept_id", 1), ("difficulty", 1), ("reviewed", 1)])
    await sessions_collection.create_index("student_id")
    await concepts_collection.create_index("unit")
