# Agente adaptativo con LangGraph

## Propósito y estado actual

Este documento describe la base inicial del agente adaptativo de LemurCopilot y el camino previsto para ampliarla.

**El agente está en desarrollo y actualmente funciona de manera local y aislada.** Su grafo usa nodos deterministas y pruebas con estudiantes construidos en memoria. No está conectado a una ruta de FastAPI, no consulta MongoDB, no recupera contenido publicado y no llama a un LLM. Tampoco reemplaza los flujos actuales de lecciones y quizzes.

La preparación de contenido pre-generado es un trabajo independiente y todavía no está lista. El agente no debe generar contenido ni depender del worker para completar una sesión. La futura integración deberá consumir únicamente contenido disponible, validado y publicado en MongoDB.

## Archivos

### Implementación

| Archivo | Responsabilidad actual |
|---|---|
| [`backend/app/agents/state.py`](../backend/app/agents/state.py) | Contrato compartido del grafo (`AgentState`), con tema, perfil resumido, estrategia, foco, solicitud de contenido y campos reservados para resultados y errores. |
| [`backend/app/agents/profile.py`](../backend/app/agents/profile.py) | Convierte el modelo `Student` ya disponible en un perfil compacto para un tema: mastery del tema, conceptos intentados y conceptos débiles. Limita los conceptos débiles a cinco, y resume misconceptions recientes y frecuentes. No accede a MongoDB. |
| [`backend/app/agents/nodes.py`](../backend/app/agents/nodes.py) | Nodos deterministas: selección de estrategia, selección de conceptos foco y creación de una especificación de solicitud de contenido. |
| [`backend/app/agents/graph.py`](../backend/app/agents/graph.py) | Construye y compila el grafo LangGraph y exporta la instancia `agent_graph`. |
| [`backend/app/agents/runner.py`](../backend/app/agents/runner.py) | Punto de entrada asíncrono que recibe un `Student`, construye el perfil e invoca el grafo. Espera recibir un estudiante previamente cargado y autenticado por el backend; no lee Mongo ni valida autenticación por sí mismo. |

### Pruebas

| Archivo | Cobertura |
|---|---|
| [`backend/tests/test_agent_nodes.py`](../backend/tests/test_agent_nodes.py) | Umbrales de estrategia, límites y valores faltantes o inválidos. |
| [`backend/tests/test_agent_profile.py`](../backend/tests/test_agent_profile.py) | Resumen por tema, conceptos débiles, misconceptions y exclusión del texto completo de las preguntas. |
| [`backend/tests/test_agent_graph.py`](../backend/tests/test_agent_graph.py) | Ejecución del grafo, preservación de entradas, selección del foco, perfil de ejemplo y runner asíncrono. |

La dependencia `langgraph` se declara en [`backend/requirements.txt`](../backend/requirements.txt) y se verificó su importación en el contenedor del backend.

## Flujo actual

```text
Student (recibido por el runner)
        │
        ▼
build_agent_profile(student, topic)
        │  perfil compacto del tema y mastery por concepto
        ▼
choose_strategy
        │  last_score < 0.60 → reinforcement
        │  last_score >= 0.85 → challenge
        │  en otro caso o sin nota válida → standard
        ▼
choose_focus
        │  toma los conceptos débiles ya priorizados por el perfil
        ▼
build_content_request
        │  tema, variante, conceptos foco, 3 preguntas
        ▼
resultado del grafo
```

La estrategia se decide con reglas locales; los conceptos débiles guían el foco, pero por ahora no cambian esa estrategia. Si no hay conceptos débiles, el foco queda vacío. La solicitud resultante es solo una estructura de datos: no ejecuta búsquedas ni carga lecciones o ejercicios.

## Mastery y forma del perfil

El perfil del agente lee el mastery general del tema (`mastery`) y el mastery por concepto (`concept_mastery`) del `Student` recibido. Por concepto puede resumir score, intentos, aciertos, errores y conteos de misconceptions. Solo considera los conceptos del tema solicitado y omite conceptos sin intentos.

`build_agent_profile` no actualiza mastery. El registro de respuestas y la actualización de estos datos pertenecen al backend existente, no al agente. El perfil tampoco incluye texto completo de preguntas falladas; limita el contexto para que sea compacto y no exponga información innecesaria al razonamiento futuro del LLM.

## Cómo ejecutar las pruebas

Con Docker Compose levantado, desde la raíz del repositorio:

```powershell
docker compose exec backend python -m unittest discover -s tests -p "test_agent_nodes.py" -v
docker compose exec backend python -m unittest discover -s tests -p "test_agent_profile.py" -v
docker compose exec backend python -m unittest discover -s tests -p "test_agent_graph.py" -v
```

Las pruebas usan datos en memoria: no requieren login, no escriben en MongoDB y no llaman a un proveedor LLM. Un test que termina con `RuntimeWarning: coroutine ... was never awaited` no ejecutó correctamente el método asíncrono; la clase de prueba debe heredar de `unittest.IsolatedAsyncioTestCase`.

## Qué está hecho y qué no

### Hecho

- Dependencia LangGraph instalada en la imagen del backend.
- Estado común del agente definido.
- Perfil resumido por tema y concepto a partir de un `Student` ya disponible.
- Selección determinista de estrategia a partir de la última nota del tema.
- Selección de conceptos débiles como foco independiente de la estrategia.
- Construcción de una especificación de recuperación con tema, variante, foco y cantidad fija de tres preguntas.
- Grafo compilado y runner asíncrono.
- Pruebas unitarias del nodo, perfil, grafo y runner.

### Pendiente

- Definir y validar las entradas del runner (tema permitido y ownership del estudiante) desde una ruta autenticada.
- Conectar el runner a una ruta/servicio backend cuando se acuerde el contrato de sesión.
- Añadir recuperación de contenido desde MongoDB, encapsulada en un servicio/nodo y limitada al release publicado, verificado y correspondiente al tema.
- Alinear el mínimo y cantidad de preguntas del agente con el formato real del quiz y la cobertura del pool publicado; el valor actual de tres es provisional y conserva el contrato del quiz actual.
- Incorporar selección/ranking de variantes y ejercicios, validaciones deterministas de elegibilidad, duplicados y cobertura de conceptos.
- Incorporar un nodo de decisión asistida por LLM solo cuando aporte valor, con salida estructurada, límites y validación. El fallback debe poder completar la decisión sin LLM.
- Registrar versión, decisiones, fallos y métricas sin guardar información innecesaria del estudiante.
- Integrar la sesión en frontend y probar ownership, desbloqueos, publicación y compatibilidad.

## Integración futura con contenido pre-generado y LLM

La integración se hará después de que el pipeline de contenido tenga releases utilizables y revisados. La secuencia prevista es:

1. El endpoint autenticado comprueba ownership y desbloqueo del tema y entrega al servicio el `Student` validado.
2. El runner genera el perfil resumido y el grafo propone estrategia, foco y requisitos de contenido.
3. Un nodo de recuperación encapsula el acceso a MongoDB y consulta solo contenido verificado y publicado del release activo. La fuente de contenido no se sustituye por generación en tiempo de petición.
4. Si se incorpora un LLM para decidir entre candidatos, este recibe un conjunto acotado de opciones elegibles y contexto pedagógico resumido. No puede inventar IDs ni saltarse los filtros deterministas.
5. Un nodo validador confirma la pertenencia al tema y al release, publicación/verificación, formato, cantidad y selección válida. Si falla, se aplica fallback determinista o se devuelve un error controlado.
6. El backend persiste la sesión con el release y las decisiones relevantes y devuelve el contrato que consume el cliente.

**Condición de seguridad funcional:** si no hay pool publicado suficiente, el agente no activa el worker ni genera contenido para el estudiante. La disponibilidad de contenido debe resolverse en el pipeline offline o mediante un fallback explícito acordado.

El chatbot RAG existente seguirá siendo un servicio separado; esta etapa no lo incorpora al grafo adaptativo.
