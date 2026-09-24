import os

from pymongo import AsyncMongoClient
from sentence_transformers import SentenceTransformer


MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["MONGODB_DATABASE"]

client = AsyncMongoClient(MONGODB_URI)

database = client[DATABASE_NAME]
collection = database["manual_chunks"]


embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


async def search_manual(query: str, limit: int = 3):
    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 10,
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 0,
                "topic": 1,
                "title": 1,
                "page": 1,
                "chunk_index": 1,
                "text": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                },
            }
        },
    ]

    results = await collection.aggregate(pipeline).to_list()

    return results