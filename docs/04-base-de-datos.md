# 04 · Base de Datos (MongoDB Atlas)

> [← Volver al índice](./README.md)

LemurCopilot usa **MongoDB Atlas** con un doble rol:

1. **Base transaccional** — estudiantes, conceptos, ejercicios, sesiones.
2. **Base vectorial** — la colección `manual_chunks` almacena embeddings y se consulta con búsqueda semántica (`$vectorSearch`) mediante un índice vectorial de Atlas.

El acceso se realiza con `AsyncMongoClient` (API async nativa de `pymongo`), con un único cliente compartido definido en [`database.py`](../backend/app/database.py).

---

## 4.1 Vista general de colecciones

```mermaid
erDiagram
    STUDENTS ||--o{ SESSIONS : "tiene"
    CONCEPTS ||--o{ EXERCISES : "evalúa"
    SESSIONS ||--o{ EXERCISES : "registra intentos de"
    MANUAL_CHUNKS ||--o{ CONCEPTS : "fundamenta (source_refs)"
    CONTENT_RELEASES ||--o{ GENERATED_LESSONS : "versiona"
    CONTENT_RELEASES ||--o{ CONTENT_JOBS : "agrupa"
    CONTENT_RELEASES ||--o{ EXERCISES : "publica"

    STUDENTS {
        ObjectId _id PK
        string google_sub UK
        string email UK
        string name
        string picture
        datetime created_at
        datetime last_login
        string current_unit
        object mastery
    }
    CONCEPTS {
        ObjectId _id PK
        string unit
        string name
        string description
        array prerequisites
        array source_refs
    }
    EXERCISES {
        ObjectId _id PK
        ObjectId concept_id FK
        string type
        string question
        array options
        string correct_answer
        float difficulty
        string generated_by
        array source_chunk_ids
        array concept_tags
        array misconception_tags
        string cognitive_skill
        string content_version
        string prompt_version
        string verification_version
        string release_id FK
        string status
        bool verified
        bool reviewed
        datetime created_at
        int times_served
        int times_correct
        int times_incorrect
    }
    SESSIONS {
        ObjectId _id PK
        ObjectId student_id FK
        datetime started_at
        array messages
        array exercises_attempted
    }
    GENERATED_LESSONS {
        ObjectId _id PK
        string topic
        string variant
        string release_id FK
        object lesson
        bool verified
        string status
    }
    CONTENT_RELEASES {
        ObjectId _id PK
        string release_id UK
        string content_version
        string status
        datetime published_at
    }
    CONTENT_JOBS {
        ObjectId _id PK
        string job_id
        string release_id FK
        string topic
        string status
        float duration_seconds
    }
    MANUAL_CHUNKS {
        ObjectId _id PK
        string course
        string unit
        string topic
        string title
        string source
        int page
        int chunk_index
        string text
        array embedding
    }
```

> Las colecciones `concepts`, `exercises` y `sessions` forman el banco compartido y el historial del motor adaptativo. Los quizzes nuevos persisten `exercise_id` para seleccionar preguntas por estudiante y calcular cobertura del pool.

---

## 4.2 Esquemas en detalle

Los modelos de referencia viven en [`backend/app/models.py`](../backend/app/models.py) (Pydantic v2). Convención: `_id` (BSON `ObjectId`) se mapea a `id: str` en Python/JSON vía `MongoBaseModel`.

### 4.2.1 `students` — identidad y modelo del estudiante

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `google_sub` | string | **Clave de identidad estable** (claim `sub` de Google). Inmutable tras creación. |
| `email` | string | Único; actualizable en cada login (puede cambiar en la cuenta Google). |
| `name` / `picture` | string | Perfil visible; `picture` opcional. |
| `created_at` / `last_login` | datetime | Auditoría de ciclo de vida. |
| `current_unit` | string \| null | Unidad en la que está trabajando. |
| `mastery` | objeto (`dict[str, MasteryEntry]`) | **Modelo de dominio**: mapa `topic` (`C1.1`, `C1.2`, …) → `{ score, last_score, best_score, attempts, last_seen }`. Nace vacío. |

Escritura: únicamente por `upsert_student_from_google()` (`$set` perfil + `$setOnInsert` identidad).

### 4.2.2 `concepts` — grafo de conocimiento

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `unit` | string | Unidad curricular (índice simple). |
| `name` / `description` | string | Nombre y descripción del concepto. |
| `prerequisites` | ObjectId[] | Aristas del grafo: conceptos previos requeridos. |
| `source_refs` | ObjectId[] | Referencias a chunks del manual que fundamentan el concepto. |

### 4.2.3 `exercises` — banco de ejercicios con métricas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `topic` | string | Pool curricular al que pertenece la pregunta (`C1.1`, `C1.2`, …). |
| `concept_id` | ObjectId o null | Concepto evaluado, opcional mientras el catálogo de conceptos no esté conectado al quiz. |
| `type` | enum | `multiple_choice` \| `true_false` \| `open`. |
| `question` / `options` / `correct_index` | — | Enunciado, alternativas y posición de la solución. |
| `explanation` | string o null | Explicación pedagógica mostrada tras responder. |
| `difficulty` | float (0–1) | Dificultad objetivo; selección con tolerancia ±0.15. |
| `generated_by` | enum | `llm` \| `manual`. |
| `source_chunk_ids` | ObjectId[] | Trazabilidad al manual. |
| `fingerprint` | string | Huella única para impedir duplicados exactos; el worker incluye el release en la huella para aislar versiones. |
| `concept_tags` / `misconception_tags` | string[] | Conceptos evaluados y errores conceptuales frecuentes asociados. Opcionales para los ejercicios históricos. |
| `cognitive_skill` | enum | Habilidad `recall`, `comprehension`, `application` o `analysis`. |
| `content_version` / `prompt_version` / `verification_version` | string | Versiones del contenido, prompt y verificador utilizados. |
| `release_id` | string \| null | Release que contiene el ejercicio. Las preguntas anteriores a releases no tienen este campo. |
| `status` / `verified` | enum / bool | Ciclo de generación y verificación (`ready` es candidato validado; no implica release publicado). |
| `reviewed` | bool | Las preguntas generadas automáticamente se publican tras validación estructural y deduplicación. |
| `times_served` / `times_correct` / `times_incorrect` | int | Métricas de uso: reparten desgaste (máx. 20 servidos) y permiten recalibrar `difficulty`. |

### 4.2.4 `generated_lessons`, `content_releases` y `content_jobs`

`generated_lessons` mantiene hasta tres variantes (`standard`, `reinforcement`, `challenge`) por tema, idioma y release. Cada documento conserva las fuentes del manual, las versiones de generación y verificación y el estado del contenido. `content_releases` agrupa los documentos y avanza por `building`, `validating`, `ready` y `published`; `content_jobs` registra cada ejecución por tema, intentos, error, duración y conteos. La publicación para estudiantes aún no se activa: el worker deja los elementos verificados en `ready`.

### 4.2.5 `sessions` — historial de interacción

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `student_id` | ObjectId | Dueño de la sesión (índice simple). |
| `started_at` | datetime | Inicio. |
| `messages` | subdocumentos[] | `{ role: agent\|student, content, timestamp }`. |
| `quiz_topic` / `score` | string / float | Tema y resultado del quiz completo. |
| `answers` | subdocumentos[] | `{ exercise_id, selected_index, correct_index, is_correct, timestamp }` — historial por pregunta. |

### 4.2.6 `manual_chunks` — corpus RAG (colección activa principal)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `course` | string | Identificador del curso (`clase-b-conaset-2024`). Permite convivencia de varios manuales. |
| `unit` | string | Unidad (`C1`, `C2`, …). |
| `topic` | string | **Clave de negocio** (`C1.1`, `C2.2`, …): une la ingesta, `LESSON_CONFIGS` y el `course.ts` del frontend. |
| `title` | string | Título del tema. |
| `source` | string | Documento fuente (`manual_conduccion_clase_b`). |
| `page` | int | Página impresa del manual → **citación** en la UI. |
| `chunk_index` | int | Orden del fragmento dentro de la página. |
| `text` | string | Contenido (ventanas de ~900 caracteres, solape 150). |
| `embedding` | float[384] | Vector generado con MiniLM multilingüe, **normalizado** (similitud coseno). |

Escritura: solo `scripts/ingest_manual.py` (borrado selectivo por `(course, topic)` + inserción).

---

## 4.3 Índices

### 4.3.1 Índices transaccionales (creados por `ensure_indexes()` al arrancar)

| Colección | Índice | Tipo | Motivo |
|-----------|--------|------|--------|
| `students` | `email` | único | Deduplicación por correo |
| `students` | `google_sub` | único | Clave de login (upsert) |
| `exercises` | `(concept_id, difficulty, reviewed)` | compuesto | Query exacta del selector adaptativo |
| `exercises` | `fingerprint` | único disperso | Deduplicación por pregunta y versión/release |
| `exercises` | `(topic, reviewed, difficulty)` | compuesto | Selección del pool por tema |
| `exercises` | `(topic, language, status, release_id)` | compuesto | Pool candidato por tema y release |
| `exercises` | `(topic, concept_tags)` | compuesto | Filtro curricular por concepto |
| `generated_lessons` | `(topic, language, status, release_id, variant)` | compuesto | Búsqueda por estado y release |
| `generated_lessons` | `(topic, language, release_id, variant)` | único | Una variante por tema e idioma en cada release |
| `content_releases` | `release_id` | único | Identidad del release |
| `content_jobs` | `(status, next_retry_at)` / `(release_id, topic)` | compuesto | Reintentos y estado de trabajos |
| `sessions` | `student_id` | simple | Historial por estudiante |
| `sessions` | `answers.exercise_id` | simple | Cobertura y anti-repetición por pregunta |
| `concepts` | `unit` | simple | Listados por unidad |

### 4.3.2 Índice vectorial (se crea **manualmente en Atlas**, fuera del código)

La búsqueda semántica requiere un índice de tipo **vectorSearch** llamado exactamente `vector_index` sobre `manual_chunks`:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

> ⚠️ **Dependencia operativa crítica:** si el índice no existe o tiene otro nombre, `search_manual()` falla en runtime. Debe crearse en Atlas UI → *Search Indexes* (o vía Atlas API). Como los embeddings se normalizan (`normalize_embeddings=True`), la similitud coseno equivale al producto punto.

La consulta que lo usa (`rag_service.py`):

```python
{
  "$vectorSearch": {
    "index": "vector_index",
    "path": "embedding",
    "queryVector": <vector de la consulta>,
    "numCandidates": 10,   # vecinos evaluados por el índice ANN
    "limit": limit         # 3 en /rag, 5 en chat
  }
}
```

---

## 4.4 Ciclo de vida de los datos

```mermaid
flowchart TB
    PDF["manual.pdf<br/>(CONASET)"] --> ING["ingest_manual.py<br/>(local, manual)"]
    ING -->|"delete_many + insert_many<br/>por (course, topic)"| CHUNKS["manual_chunks"]

    GOOGLE["Login Google"] --> AUTH["auth_service<br/>upsert"] --> STU["students"]

    CHUNKS -->|"get_topic_chunks (sin embedding)"| LESSON["Generación lección/quiz"]
    CHUNKS -->|"$vectorSearch"| CHAT["Chat / RAG"]

    subgraph Futuro["Motor adaptativo (modelado, sin endpoints)"]
        STU -.-> SESS["sessions"]
        SESS -.-> EX["exercises"]
        EX -.->|"recalibrar difficulty"| EX
    end
```

| Colección | Escritor | Lectores |
|-----------|----------|----------|
| `manual_chunks` | Script de ingesta (local) | `content_service`, `rag_service` |
| `students` | `auth_service` (upsert en login) | `auth_service` |
| `concepts` | *(aún nadie)* | *(aún nadie)* |
| `exercises` | `exercise_service` (generación + métricas) | `exercise_service` |
| `sessions` | *(aún nadie)* | `exercise_service` (anti-repetición) |

---

## 4.5 Decisiones y notas operativas

- **Sin esquema estricto a nivel Mongo**: la validación vive en la capa de aplicación (Pydantic). Los modelos son el contrato; Mongo no fuerza `validators`.
- **`mastery` como mapa embebido**: evita una colección extra y una join por estudiante; escala bien porque el número de conceptos por curso es acotado.
- **Trazabilidad RAG → ejercicios**: `source_chunk_ids` permitirá auditar de qué fragmentos del manual salió cada ejercicio generado.
- **Anti-fatiga del banco de ejercicios**: `times_served < 20` + orden ascendente reparte el uso entre ejercicios equivalentes.
- **El índice vectorial no está en `ensure_indexes()`** a propósito: los índices vectoriales de Atlas no se crean por el driver, sino por la API/UI de Atlas Search.

---

> **Siguiente:** [05 - Pipeline RAG →](./05-pipeline-rag.md)
