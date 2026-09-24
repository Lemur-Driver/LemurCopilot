import os

from pymongo import AsyncMongoClient
from sentence_transformers import SentenceTransformer
from app.services.llm_service import generate_text

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
    
    cursor = await collection.aggregate(pipeline)
    results = await cursor.to_list()

    return results


async def ask_manual(query: str, limit: int = 3):
    results = await search_manual(query, limit)

    context = "\n\n".join(
        [
            f"""
Fuente: {result["title"]}
Página: {result["page"]}

{result["text"]}
"""
            for result in results
        ]
    )

    prompt = f"""
Eres un tutor de conducción para estudiantes que preparan
el examen de licencia Clase B en Chile.

Debes responder la pregunta del estudiante utilizando
únicamente la información proporcionada en el contexto
del manual oficial.

No infieras relaciones entre números, porcentajes,
tablas o gráficos si el contexto no establece
explícitamente esa relación.

No atribuyas un porcentaje a una categoría
si el texto proporcionado no indica explícitamente
que ese porcentaje corresponde a esa categoría.

Si la información está incompleta o ambigua,
indícalo.

Al generar la respuesta no digas cosas como "de acuerdo al contexto"
o de "en base de..." responde con seguridad y citas que la información fue extraida del manual al final.

Contexto del manual:

{context}

Pregunta del estudiante:

{query}

Responde de manera clara, breve y didáctica.
"""

    answer = await generate_text(prompt)

    return {
        "answer": answer,
        "sources": results,
    }