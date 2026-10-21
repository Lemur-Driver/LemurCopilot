# 07 · Flujos End-to-End

> [← Volver al índice](./README.md)

Diagramas de secuencia de los cuatro flujos principales del sistema, desde la acción del usuario hasta la persistencia. Actores abreviados:

- **👤** Estudiante · **FE** Frontend (React) · **BE** Backend (FastAPI)
- **🗄️** MongoDB Atlas · **🤖** LLM (Ollama/Gemini) · **🔐** Google

---

## 7.1 Flujo de autenticación con Google

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 Estudiante
    participant FE as Frontend (Login)
    participant G as 🔐 Google (GIS + OAuth)
    participant BE as Backend (/auth)
    participant DB as 🗄️ students

    U->>FE: Clic en "Sign in with Google"
    FE->>G: renderButton + initialize (VITE_GOOGLE_CLIENT_ID)
    G-->>U: Popup de consentimiento
    U->>G: Elige cuenta y autoriza
    G-->>FE: callback(credential = id_token JWT)
    Note over FE: El JWT NO se decodifica<br/>en el cliente
    FE->>BE: POST /auth/google { credential }
    BE->>G: verify_oauth2_token(credential, audience=GOOGLE_CLIENT_ID)
    alt Token inválido / expirado / email no verificado
        G-->>BE: Error de verificación
        BE-->>FE: 401 { detail }
        FE-->>U: "No pudimos iniciar sesión…"
    else Token válido
        G-->>BE: claims { sub, email, name, picture }
        BE->>DB: find_one_and_update(google_sub,<br/>$set perfil, $setOnInsert identidad, upsert=true)
        DB-->>BE: documento Student (AFTER)
        BE-->>FE: 200 { id, google_sub, email, name, picture }
        FE->>FE: navigate('/')  (TODO: persistir sesión propia)
    end
```

**Puntos clave:**
- La verificación criptográfica ocurre **solo en backend** (firma + audiencia + expiración + `email_verified`).
- `google_sub` es la clave de identidad inmutable; el perfil se actualiza en cada login.
- El mismo endpoint sirve para registro (primer login) y login recurrente (upsert).

---

## 7.2 Flujo de contenido publicado y quiz

La lección se genera durante el ciclo offline del worker; el frontend lee su versión publicada y solicita por separado tres preguntas del pool publicado. Las peticiones del estudiante no generan preguntas ni llaman al LLM para crear el pool.

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 Estudiante
    participant FE as Frontend (Lesson.tsx)
    participant BE as Backend (/lessons)
    participant DB as 🗄️ MongoDB
    participant LLM as 🤖 LLM
    participant Worker as ⚙️ content-worker

    rect rgb(245, 245, 245)
        Note over Worker,DB: Preparación offline, previa al acceso del estudiante
        Worker->>DB: Leer manual_chunks y configuración del tema
        Worker->>Worker: Generar y verificar lecciones y pool de preguntas
        Worker->>DB: Guardar release en ready
        Worker->>DB: Validar y publicar release; actualizar content_catalog
    end
    U->>FE: Abre clase (C1.2)
    FE->>FE: Busca clase en course.ts
    FE->>BE: POST /lessons/generate/C1.2
    BE->>DB: Resolver release publicado y leer lección standard
    DB-->>BE: Lección + fuentes
    BE-->>FE: 200 { topic, lesson, sources }
    FE->>FE: Renderiza lección + fuentes citadas
    U->>FE: Clic "Tomar quiz"
    FE->>BE: POST /lessons/C1.2/quiz
    BE->>DB: Resolver release activo y seleccionar preguntas publicadas verificadas
    alt No hay release o pool elegible insuficiente
        BE-->>FE: 503; generar/publicar pool con content-worker
    else Pool disponible
        BE->>DB: Guardar sesión con release_id y preguntas asignadas
        BE-->>FE: quiz { sessionId, questions }
        FE->>FE: Monta <Quiz/> con exerciseId
        U->>FE: Responde las 3 preguntas
        FE->>BE: POST /students/me/quiz-answer (por pregunta)
        BE->>DB: Corregir contra ejercicio asignado
        FE->>BE: POST /students/me/quiz-results
        BE->>DB: Actualizar mastery y finalizar sesión
    end
```

**Puntos clave:**
- El worker genera preguntas RAG y las deja en `ready`; la validación y publicación las hacen elegibles para el estudiante.
- Las **fuentes** (páginas del manual) viajan deduplicadas para citación en la UI.
- El endpoint online asigna solamente preguntas del release activo, verificadas y publicadas; no invoca al LLM.
- El backend corrige las respuestas usando el pool persistido; el cliente solo envía `exerciseId` y `selectedIndex`.

---

## 7.3 Flujo del chat tutor (streaming)

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 Estudiante
    participant FE as Frontend (ChatWidget)
    participant BE as Backend (/chat)
    participant DB as 🗄️ manual_chunks
    participant LLM as 🤖 LLM

    U->>FE: Escribe pregunta y envía
    FE->>FE: Burbuja usuario + burbuja asistente vacía
    FE->>BE: POST /chat/stream { message, history[-10:] }
    BE->>LLM: Clasificador de dominio (JSON)
    LLM-->>BE: {"classification": …}

    alt OUT_OF_DOMAIN (o JSON de clasificador inválido)
        BE-->>FE: evento sources: []
        BE-->>FE: token: "Estoy especializado en conducción…" + done
        FE-->>U: Mensaje fijo del guardrail
    else IN_DOMAIN
        BE->>DB: $vectorSearch(query_embedding, limit=5)
        DB-->>BE: chunks + scores
        alt Sin resultados
            BE-->>FE: sources: [] + token "No encontré información…" + done
        else Con resultados
            BE-->>FE: evento sources [tema, título, página, score]
            FE->>FE: Adjunta fuentes a la burbuja
            BE->>LLM: stream_text(prompt + contexto + historial)
            loop Por cada fragmento generado
                LLM-->>BE: chunk de texto
                BE-->>FE: evento token { content }
                FE->>FE: Concatena a la burbuja en vivo
            end
            BE-->>FE: evento done
            FE->>FE: Habilita input
        end
    end
```

**Puntos clave:**
- Protocolo NDJSON: un JSON por línea; el frontend despacha por `type` (`sources`, `token`, `done`, `error`).
- **Doble recorte de historial**: el widget envía máx. 10 y el servidor vuelve a recortar (defensa en profundidad).
- Las respuestas del guardrail y de "sin contexto" **no gastan generación**: viajan como un único token.
- Cabeceras anti-buffering para que los tokens lleguen en tiempo real.

---

## 7.4 Flujo offline de ingesta del manual

Proceso operativo ejecutado a mano por el equipo (no forma parte del runtime de los contenedores):

```mermaid
sequenceDiagram
    autonumber
    participant OP as 🧑‍💻 Operador
    participant SC as ingest_manual.py
    participant PDF as 📕 manual.pdf
    participant EMB as 🧠 SentenceTransformer
    participant DB as 🗄️ manual_chunks

    OP->>SC: python -m app.scripts.ingest_manual (local)
    SC->>PDF: Extracción página a página (PyMuPDF)
    PDF-->>SC: textos crudos
    SC->>SC: clean_text() por página
    SC->>SC: validate_topics() (rangos válidos)
    loop Por cada tema en TOPICS
        SC->>SC: Filtrar páginas del tema + chunking (900/150)
        SC->>EMB: encode(chunks, normalize=True)
        EMB-->>SC: embeddings[384]
        alt Tema sin chunks (fallo)
            SC->>SC: ⚠ Saltar — MongoDB queda intacta
        else Chunks OK
            SC->>DB: delete_many({course, topic})
            SC->>DB: insert_many(chunks con embedding)
        end
    end
    SC-->>OP: Resumen (chunks por tema, eliminados, total)
```

**Post-requisito manual:** el índice `vector_index` de Atlas Search debe existir (se crea una vez por clúster, ver [04 - Base de datos](./04-base-de-datos.md#432-índice-vectorial-se-crea-manualmente-en-atlas-fuera-del-código)).

---

## 7.5 Vista combinada: quién llama a quién

```mermaid
flowchart LR
    subgraph FE["Frontend"]
        LoginP["Login"] -.->|usa| GSI["GoogleSignInButton"]
        HomeP["Home"] --> LP["LearningPath"] --> LC["LessonCard"]
        LessonP["Lesson"] --> QuizC["Quiz"]
        ChatW["ChatWidget"]
    end

    GSI == "POST /auth/google" ==> AuthR["routes/auth"]
    LessonP == "POST /lessons/generate/:topic" ==> LessonsR["routes/lessons"]
    ChatW == "POST /chat/stream" ==> ChatR["routes/chat"]

    AuthR --> AuthS["auth_service"]
    LessonsR --> ContentS["content_service"]
    LessonsR --> LessonS["lesson_service"]
    LessonsR --> QuizS["quiz_service"]
    ChatR --> ChatS["chat_service"]
    ChatS --> RAGS["rag_service"]

    LessonS --> LLMS["llm_service"]
    QuizS --> LLMS
    ChatS --> LLMS

    AuthS --> DB[("MongoDB")]
    ContentS --> DB
    RAGS --> DB
    RAGS --> EMB["SentenceTransformer"]
    LLMS --> OLL["Ollama"] & GEM["Gemini"]
    AuthS --> GOOG["Google OAuth"]
```

---

> **Siguiente:** [08 - Despliegue y configuración →](./08-despliegue-y-configuracion.md)
