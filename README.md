# LemurCopilot
Sistema de tutoría adaptativa (Enfoque: Licencia de conducir Chile)

Herramienta complementaria de preparación para el examen teórico y aprendizaje de educación vial.

El sistema construye un modelo del conocimiento del estudiante y utiliza un agente para adaptar dinámicamente la enseñanza, ejercicios y evaluaciones, fundamentándose en material oficial chileno.

## Stack

- React + TypeScript + Vite
- FastAPI
- MongoDB Atlas
- Sentence Transformers
- Ollama / Gemini
- Docker

## Flujo principal

Usuario selecciona una clase
→ React llama FastAPI
→ Backend recupera chunks desde MongoDB
→ LLM genera lección
→ LLM genera quiz
→ React renderiza ambos.

## Ejecutar

docker compose up --build

Frontend:
http://localhost:5173

Backend:
http://localhost:8000

Swagger:
http://localhost:8000/docs


## 📄 Licencia y Propiedad Intelectual

Este proyecto ha sido desarrollado de manera conjunta por **Brendan Rubilar Vivanco** y **Tomás Cid Muñoz**. 

El código fuente se encuentra alojado en este repositorio de forma pública únicamente con fines de **evaluación técnica y muestra de arquitectura**. 

Todos los derechos sobre el software, la lógica de negocio y los componentes visuales están reservados. No está permitida su copia, distribución ni utilización sin la autorización expresa de los autores. Consulta el archivo [LICENSE](./LICENSE) para más detalles.
