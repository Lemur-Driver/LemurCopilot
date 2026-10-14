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
generated_lessons_collection = database["generated_lessons"]
content_releases_collection = database["content_releases"]
content_jobs_collection = database["content_jobs"]
content_catalog_collection = database["content_catalog"]


async def ensure_indexes() -> None:
    await students_collection.create_index("email", unique=True)
    await students_collection.create_index("google_sub", unique=True)
    await exercises_collection.create_index([("concept_id", 1), ("difficulty", 1), ("reviewed", 1)])
    await exercises_collection.create_index("fingerprint", unique=True, sparse=True)
    await exercises_collection.create_index([("topic", 1), ("reviewed", 1), ("difficulty", 1)])
    await exercises_collection.create_index([("topic", 1), ("language", 1), ("status", 1), ("release_id", 1)])
    await exercises_collection.create_index([("topic", 1), ("concept_tags", 1)])
    await generated_lessons_collection.create_index(
        [("topic", 1), ("language", 1), ("status", 1), ("release_id", 1), ("variant", 1)]
    )
    await generated_lessons_collection.create_index(
        [("topic", 1), ("language", 1), ("release_id", 1), ("variant", 1)], unique=True
    )
    await content_releases_collection.create_index("release_id", unique=True)
    await content_releases_collection.create_index("status")
    await content_catalog_collection.create_index("topics.topic")
    await content_catalog_collection.create_index("topics.release_id")
    await content_jobs_collection.create_index([("status", 1), ("next_retry_at", 1)])
    await content_jobs_collection.create_index([("release_id", 1), ("topic", 1)])
    await sessions_collection.create_index("student_id")
    await sessions_collection.create_index([("student_id", 1), ("quiz_status", 1)])
    await sessions_collection.create_index("answers.exercise_id")
    await concepts_collection.create_index("unit")