from app.database import database


collection = database["manual_chunks"]

# Course lesson IDs do not always match the manual subsection labels.
TOPIC_SOURCE_MAP = {
    "C1.1": "C1.1",
    "C1.2": "C1",
    "C1.3": "C1.2",
    "C3.1": "C3",
    "C4.1": "C4",
    "C4.2": "C4.1",
    "C4.3": "C4.2",
    "C4.4": "C4.3",
    "C4.5": "C4.4",
    "C4.6": "C4.5",
    "C4.7": "C4.6",
    "C4.8": "C4.7",
    "C5.1": "C5",
    "C5.2": "C5.1",
    "C6.1": "C6",
    "C6.2": "C6.1",
    "C6.3": "C6.2",
    "C6.4": "C6.3",
    "C6.5": "C6.4",
    "C6.6": "C6.5",
    "C6.7": "C6.6",
}


async def get_topic_chunks(topic: str):
    source_topic = TOPIC_SOURCE_MAP.get(topic, topic)
    cursor = collection.find(
        {
            "topic": source_topic,
        },
        {
            "_id": 1,
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