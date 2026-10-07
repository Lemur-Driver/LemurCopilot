# 06 · Referencia de API REST

> [← Volver al índice](./README.md)

**Base URL (desarrollo):** `http://localhost:8000`
**Documentación interactiva (Swagger):** `http://localhost:8000/docs`
**Formato:** JSON UTF-8 en requests y responses (salvo el chat, que usa NDJSON en streaming).
**CORS:** solo `http://localhost:5173`.

---

## 6.1 Resumen de endpoints

| Método | Ruta | Propósito | Estado |
|--------|------|-----------|--------|
| GET | `/` | Saludo de la API | ✅ Activo |
| GET | `/health` | Healthcheck | ✅ Activo |
| POST | `/auth/google` | Login con Google (verifica `id_token`) | ✅ Activo |
| POST | `/lessons/generate/{topic}` | Genera la lección de un tema | ✅ Activo (core) |
| POST | `/lessons/{topic}/quiz` | Asigna un quiz del pool al estudiante | ✅ Activo (core) |
| POST | `/chat/stream` | Chat tutor con streaming NDJSON | ✅ Activo (core) |
| POST | `/rag/search` | Búsqueda semántica en el manual | 🧪 Exploración |
| POST | `/rag/ask` | QA directa sobre el manual | 🧪 Exploración |
| GET | `/students/mongo-test` | Ping a MongoDB | 🔧 Diagnóstico |
| GET | `/students/llm-test` | Ping al LLM | 🔧 Diagnóstico |
| POST | `/students/chat` | Eco de prompt al LLM | 🔧 Diagnóstico |

> 🔓 **Sin autenticación de peticiones todavía:** el login verifica identidad pero la API no emite ni exige sesión propia. Es deuda técnica conocida (hay `TODO` en `Login.tsx`).

---

## 6.2 Salud

### `GET /`

```json
{ "message": "Hola desde FastAPI" }
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## 6.3 Autenticación

### `POST /auth/google`

Verifica criptográficamente el `id_token` emitido por Google Identity Services y hace *upsert* del estudiante (crea o actualiza perfil + `last_login`).

**Request:**

```json
{
  "credential": "eyJhbGciOiJSUzI1NiIs...<id_token JWT de Google>"
}
```

**Response `200 OK`:**

```json
{
  "id": "665f1c2ab31f9e0a1c4d7e88",
  "google_sub": "104823456789012345678",
  "email": "estudiante@gmail.com",
  "name": "Estudiante Lemur",
  "picture": "https://lh3.googleusercontent.com/a-/..."
}
```

**Errores:**

| Código | Condición |
|--------|-----------|
| `401` | Token inválido: firma incorrecta, expirado, audiencia distinta a `GOOGLE_CLIENT_ID`, o `email_verified = false`. Detalle en `detail`. |

**Notas de seguridad:** el backend valida firma (contra las claves públicas de Google), expiración, audiencia y verificación de email. El frontend nunca decodifica el JWT.

---

## 6.4 Generación de lecciones (core)

### `POST /lessons/generate/{topic}`

Genera la mini-lección en vivo y prepara el pool de preguntas del tema. La asignación concreta del quiz se realiza mediante `POST /lessons/{topic}/quiz`, que crea una sesión vinculada al estudiante. La respuesta de generación no contiene el quiz. Sin cuerpo en el request; todo va en el path.

**Parámetros de ruta:** `topic` — código del tema (`C1.1`, `C1.2`, `C2.1`, `C2.2`, `C2.3`, …). Debe existir:
1. en `LESSON_CONFIGS` (configuración pedagógica), y
2. como `topic` con chunks en `manual_chunks` (ingestado).

**Ejemplo:**

```bash
curl -X POST http://localhost:8000/lessons/generate/C1.1
```

**Response `200 OK`:**

```json
{
  "topic": "C1.1",
  "lesson": {
    "title": "Estadísticas de siniestros en Chile",
    "introduction": "Texto introductorio de la lección…",
    "sections": [
      {
        "title": "Magnitud del problema",
        "content": "Explicación pedagógica…",
        "example": "Ejemplo concreto…"
      }
    ],
    "key_points": ["Idea clave 1", "Idea clave 2"]
  },
  "sources": [
    { "page": 8, "title": "Estadísticas de siniestros en Chile", "source": "manual_conduccion_clase_b" }
  ]
}
```

**Contratos garantizados por validación en backend:**
- `lesson.sections` ≥ 1; cada sección con `title` y `content` (`example` puede ser vacío).
- `POST /lessons/{topic}/quiz` devuelve exactamente 3 preguntas, cada una con 4 opciones y `exerciseId`; no incluye clave correcta ni explicación antes de responder.

**Errores:**

| Código | Condición |
|--------|-----------|
| `400` | `topic` sin configuración pedagógica o sin contenido en MongoDB. Mensaje explicativo en `detail`. |
| `500` | El LLM devolvió JSON inválido/estructura no conforme, o fallo interno (detalle genérico, error logueado en servidor). |

> ⏱️ **Latencia:** normalmente involucra una llamada al LLM para la lección. Solo se añade una llamada para generar preguntas cuando el pool está vacío, agotado o supera el umbral de cobertura.

### `POST /lessons/{topic}/quiz`

Asigna al estudiante autenticado tres preguntas del pool y crea una sesión de quiz. Las preguntas devueltas incluyen `exerciseId`, `question` y `options`; la clave correcta y la explicación no se envían antes de responder.

**Response `200 OK`:**

```json
{
  "quiz": {
    "sessionId": "66f...",
    "questions": [
      { "exerciseId": "66f...", "question": "¿Qué factor aumenta…?", "options": ["A", "B", "C", "D"] }
    ]
  }
}
```

### `POST /students/me/quiz-answer`

Registra una respuesta individual de la sesión activa y devuelve enseguida `correctIndex`, `isCorrect` y `explanation`. Solo acepta ejercicios asignados en la sesión del estudiante; una respuesta ya registrada no puede cambiarse.

**Request:** `{ "sessionId": "66f...", "exerciseId": "66f...", "selectedIndex": 0 }`.

### `POST /students/me/quiz-results`

**Request:** `{ "sessionId": "66f..." }`. Finaliza un quiz solo si sus tres respuestas ya quedaron registradas. El backend calcula el resultado desde esas respuestas guardadas, actualiza el progreso y marca la sesión completada.

---

## 6.5 Chat tutor con streaming (core)

### `POST /chat/stream`

Tutor conversacional con guardrail de dominio y RAG. La respuesta es un stream **NDJSON** (`application/x-ndjson`): un objeto JSON por línea.

**Request:**

```json
{
  "message": "¿Qué es la distancia de frenado?",
  "history": [
    { "role": "user", "content": "Hola" },
    { "role": "assistant", "content": "¡Hola! Soy tu tutor…" }
  ]
}
```

| Campo | Restricción |
|-------|-------------|
| `message` | 1–500 caracteres |
| `history` | Lista de `{role: user\|assistant, content: 1–2000 chars}`; el backend usa solo los últimos 10 |

**Respuesta — secuencia de eventos NDJSON:**

```
{"type":"sources","sources":[{"topic":"C2.2","title":"La energía y las leyes físicas","page":24,"score":0.8123}]}
{"type":"token","content":"La distancia"}
{"type":"token","content":" de frenado es"}
{"type":"token","content":"…"}
{"type":"done"}
```

| Evento `type` | Cuándo | Payload |
|---------------|--------|---------|
| `sources` | Siempre primero (puede ser `[]`) | Fuentes deduplicadas por página: `topic`, `title`, `page`, `score` |
| `token` | Streaming de la respuesta | `content`: fragmento de texto |
| `done` | Cierre exitoso | — |
| `error` | Fallo durante la generación | `message`: texto de error para mostrar |

**Casos especiales (respuesta directa, sin LLM generador):** si el mensaje es `OUT_OF_DOMAIN` o no hubo resultados RAG, el stream contiene `sources` vacío + un único `token` con el mensaje fijo + `done`.

**Errores HTTP:**

| Código | Condición |
|--------|-----------|
| `500` | Fallo al preparar la respuesta (antes de iniciar el stream). |

**Cabeceras de respuesta:** `Cache-Control: no-cache`, `X-Accel-Buffering: no` (evita buffering de proxies).

---

## 6.6 RAG (exploración / depuración)

### `POST /rag/search`

Búsqueda vectorial pura sobre el manual.

```json
// Request
{ "query": "distancia de detención" }

// Response 200
{
  "results": [
    {
      "topic": "C2.2",
      "title": "La energía y las leyes físicas",
      "page": 24,
      "chunk_index": 2,
      "text": "…fragmento del manual…",
      "score": 0.8341
    }
  ]
}
```

Devuelve hasta **3** resultados (parámetro interno `limit`).

### `POST /rag/ask`

QA directa: recupera contexto y responde con el prompt tutor (no streaming, no clasificador de dominio).

```json
// Request
{ "query": "¿Qué es el Sistema Seguro?" }

// Response 200
{
  "answer": "El Sistema Seguro es…",
  "sources": [ /* mismos campos que /rag/search */ ]
}
```

---

## 6.7 Diagnóstico

| Endpoint | Request | Response | Verifica |
|----------|---------|----------|----------|
| `GET /students/mongo-test` | — | `{ "mongodb": "connected" }` | Conectividad con Atlas (lanza excepción si cae) |
| `GET /students/llm-test` | — | `{ "response": "…una frase…" }` | Conectividad con el proveedor LLM |
| `POST /students/chat` | `{ "prompt": "…" }` | `{ "response": "…" }` | Round-trip de generación |

> ⚠️ Estos endpoints deberían protegerse o eliminarse en producción: permiten gasto de LLM sin autenticación.

---

## 6.8 Modelo de errores

FastAPI responde errores con el formato estándar:

```json
{ "detail": "No existe configuración pedagógica para C9.9" }
```

- `400` — regla de negocio (`ValueError` en servicios de lección).
- `401` — token de Google inválido.
- `422` — validación Pydantic del request (campos faltantes/largos inválidos), automática de FastAPI.
- `500` — fallo interno (LLM caído, JSON inválido, Mongo inalcanzable). El detalle real se loguea en consola del backend, no se expone.

---

## 6.9 Convenciones

- Todos los endpoints de acción usan `POST` (incluso la generación, que es una operación con efectos de cómputo, no una lectura idempotente cacheable).
- Fechas en ISO-8601 (`datetime.utcnow` en el servidor).
- `_id` de Mongo se serializa como `id` string.
- Los `score` del vector search son similitud coseno (0–1, mayor = más similar).

---

> **Siguiente:** [07 - Flujos end-to-end →](./07-flujos-end-to-end.md)
