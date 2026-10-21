# Agente adaptativo con LangGraph

## Propósito y estado actual

Este documento describe la base inicial del agente adaptativo de LemurCopilot y el camino previsto para ampliarla.

**El agente está en desarrollo y tiene una primera integración backend experimental.** Una ruta autenticada valida tema y desbloqueo, construye un perfil resumido del estudiante, consulta actividad reciente y el grafo determinista recupera contenido verificado del release publicado. Aún no guarda una sesión de aprendizaje ni reemplaza los flujos actuales; tampoco usa un LLM.

La preparación de contenido pre-generado es independiente. El agente no genera contenido ni activa el worker durante una petición: consume únicamente lo que ya esté disponible, validado y publicado en MongoDB.

## Archivos

### Implementación

| Archivo | Responsabilidad actual |
|---|---|
| [`backend/app/agents/state.py`](../backend/app/agents/state.py) | Contrato compartido del grafo (`AgentState`), con tema, perfil resumido, estrategia, foco, solicitud de contenido y campos reservados para resultados y errores. |
| [`backend/app/agents/profile.py`](../backend/app/agents/profile.py) | Convierte el modelo `Student` autenticado en un perfil compacto. Normaliza los temas (`C1.2` → `C1_2`) según las claves persistidas; resume mastery, conceptos débiles y misconceptions sin incluir texto de preguntas. |
| [`backend/app/agents/nodes.py`](../backend/app/agents/nodes.py) | Nodos deterministas para estrategia y foco; crea la solicitud y llama al servicio de recuperación de contenido. Usa la nota reciente del tema como fallback si falta `last_score` en el perfil de mastery. |
| [`backend/app/agents/graph.py`](../backend/app/agents/graph.py) | Construye y compila el grafo LangGraph: estrategia → foco → solicitud → recuperación. |
| [`backend/app/agents/runner.py`](../backend/app/agents/runner.py) | Recibe un `Student` ya autenticado, valida el tema, genera perfil, añade los últimos diez quizzes completados y ejecuta el grafo. |
| [`backend/app/services/agent_activity_service.py`](../backend/app/services/agent_activity_service.py) | Lee actividad de quizzes por `student_id`, únicamente completos y con proyección acotada; no retorna mensajes ni texto de preguntas. |
| [`backend/app/services/agent_content_service.py`](../backend/app/services/agent_content_service.py) | Recupera lección y ejercicios del release publicado; valida cada ejercicio y rankea hasta tres por cobertura de conceptos, exposición y dificultad, sin crear asignaciones ni modificar contadores. |
| [`backend/app/routes/agent.py`](../backend/app/routes/agent.py) | Ruta autenticada `POST /agent/{topic}/plan`, valida tema y desbloqueo y devuelve la decisión, contenido y errores de disponibilidad. |

### Pruebas

| Archivo | Cobertura |
|---|---|
| [`backend/tests/test_agent_nodes.py`](../backend/tests/test_agent_nodes.py) | Umbrales de estrategia, límites y valores faltantes o inválidos. |
| [`backend/tests/test_agent_profile.py`](../backend/tests/test_agent_profile.py) | Resumen por tema, conceptos débiles, misconceptions y exclusión del texto completo de las preguntas. |
| [`backend/tests/test_agent_graph.py`](../backend/tests/test_agent_graph.py) | Ejecución asíncrona del grafo y del runner; perfil, actividad simulada y rechazo de temas desconocidos. |
| [`backend/tests/test_agent_content_service.py`](../backend/tests/test_agent_content_service.py) | Elegibilidad, ranking determinista, release publicado, fallback a lección estándar y pool insuficiente. |

La dependencia `langgraph` se declara en [`backend/requirements.txt`](../backend/requirements.txt) y se verificó su importación en el contenedor del backend.

## Flujo actual

```text
get_current_student (token autenticado)
        │
        ├── mastery y conceptos (claves C1.2 → C1_2)
        └── últimos 10 quizzes completados (sin mensajes/preguntas)
                │
                ▼
          build_agent_profile
                ▼
          choose_strategy
          nota < 0.60 → reinforcement
          nota >= 0.85 → challenge
          reciente del mismo tema si falta last_score; si no → standard
                ▼
            choose_focus
                ▼
       build_content_request
                ▼
          retrieve_content
          release activo → lección verificada + pool publicado
          filtra y rankea hasta 3 ejercicios
                ▼
     respuesta del endpoint /agent/{topic}/plan
```

La recuperación no llama al selector de quiz existente porque este crea una asignación y actualiza `times_served`. El servicio del agente solo lee documentos, exige tema/release/estado/verificación/revisión elegibles y devuelve ejercicios solo si hay tres. Si falta la variante elegida intenta la lección `standard`; si falta release, lección o pool, retorna una respuesta sin contenido parcial y un error acotado. No activa worker ni genera material.

## Ruta HTTP y contrato actual

`POST /agent/{topic}/plan` requiere el bearer token de LemurCopilot. La ruta obtiene al estudiante autenticado mediante `get_current_student`, confirma que el tema exista en `LESSON_CONFIGS` y esté desbloqueado, y recién entonces ejecuta el runner. No acepta un `student_id` del cliente.

La respuesta incluye `topic`, `strategy`, motivos de decisión/foco, `contentRequest`, `releaseId`, `lesson`, `lessonVariant`, `exercises` y `contentErrors`. Los ejercicios se proyectan a un DTO público con ID, enunciado, opciones, conceptos y dificultad; no se retornan campos internos ni la clave correcta.

## Mastery y forma del perfil

El perfil del agente lee el mastery general del tema (`mastery`) y el mastery por concepto (`concept_mastery`) del `Student` recibido. Por concepto puede resumir score, intentos, aciertos, errores y conteos de misconceptions. Solo considera los conceptos del tema solicitado y omite conceptos sin intentos.

`build_agent_profile` no actualiza mastery. El registro de respuestas y la actualización de estos datos pertenecen al backend existente, no al agente. El perfil tampoco incluye texto completo de preguntas falladas; limita el contexto para que sea compacto. La actividad reciente se consulta aparte en `agent_activity_service` con filtro por el estudiante autenticado, estado `completed`, orden por `completed_at` y límite de diez. Solo se proyectan tema, fecha, nota y aciertos/errores; por ahora la nota reciente del mismo tema puede alimentar la estrategia cuando el mastery no trae `last_score`.

## Cómo ejecutar las pruebas

Con Docker Compose levantado, desde la raíz del repositorio:

```powershell
docker compose exec backend python -m unittest discover -s tests -p "test_agent*.py" -v
```

Las pruebas usan datos en memoria: no requieren login, no escriben en MongoDB y no llaman a un proveedor LLM. Un test que termina con `RuntimeWarning: coroutine ... was never awaited` no ejecutó correctamente el método asíncrono; la clase de prueba debe heredar de `unittest.IsolatedAsyncioTestCase`.

## Qué está hecho y qué no

### Hecho

- Dependencia LangGraph instalada en la imagen del backend.
- Estado común del agente definido.
- Perfil resumido por tema y concepto a partir de un `Student` autenticado, usando la clave Mongo normalizada (`C1_2`).
- Endpoint autenticado para obtener el plan del agente con validación de tema y desbloqueo.
- Resumen de hasta diez quizzes completos del propio estudiante autenticado.
- Recuperación de la lección elegida (fallback a standard) y hasta tres ejercicios elegibles del release publicado, con ranking determinista de foco, exposición y dificultad.
- Fallback seguro ante fallos de la consulta de contenido y respuesta explícita cuando el release o el pool no está disponible.
- Selección determinista de estrategia a partir de la última nota del tema.
- Selección de conceptos débiles como foco independiente de la estrategia.
- Construcción de una especificación de recuperación con tema, variante, foco y cantidad fija de tres preguntas.
- Grafo compilado y runner asíncrono.
- Pruebas unitarias de actividad, elegibilidad/ranking de contenido, nodo, perfil, grafo y runner.

### Pendiente

- Guardar una sesión persistida con estudiante, release, estrategia, variante y referencias de ejercicios; aún no existe `POST /learning-sessions/{topic}`.
- Validar cobertura mínima por conceptos y ajustar selección a una política pedagógica acordada; el selector actual cubre focos de forma greedy y después usa exposición/dificultad.
- Añadir elección asistida por LLM solo si agrega valor, con salida estructurada y fallback determinista.
- Registrar versiones, latencias y decisiones de forma inspeccionable.
- Integrar la sesión en frontend y probar ownership, desbloqueos, publicación y compatibilidad.

## Integración futura con contenido pre-generado y LLM

La integración pendiente consiste en persistir una sesión de aprendizaje con release y ejercicios seleccionados. Luego puede integrarse al frontend el DTO seguro actual y evaluarse un nodo LLM, siempre limitado a candidatos recuperados y validados por el backend; el LLM no puede elegir IDs ajenos al release ni generar contenido.

**Condición de seguridad funcional:** si no hay pool publicado suficiente, el agente no activa el worker ni genera contenido para el estudiante. La disponibilidad de contenido debe resolverse en el pipeline offline o mediante un fallback explícito acordado.

El chatbot RAG existente seguirá siendo un servicio separado; esta etapa no lo incorpora al grafo adaptativo.
