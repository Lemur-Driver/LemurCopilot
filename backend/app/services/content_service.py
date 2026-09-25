from app.database import database


collection = database["manual_chunks"]


async def get_topic_chunks(topic: str):
    cursor = collection.find(
        {
            "topic": topic,
        },
        {
            "_id": 0,
            "course": 1,
            "unit": 1,
            "topic": 1,
            "title": 1,
            "source": 1,
            "page": 1,
            "chunk_index": 1,
            "text": 1,
        },
    ).sort(
        [
            ("page", 1),
            ("chunk_index", 1),
        ]
    )

    results = await cursor.to_list()

    return results