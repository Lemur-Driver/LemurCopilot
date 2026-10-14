# LemurCopilot
Sistema de tutoría adaptativa (Enfoque: Licencia de conducir Chile)

Herramienta complementaria de preparación para el examen teórico y aprendizaje de educación vial.

El sistema construye un modelo del conocimiento del estudiante y utiliza un agente para adaptar dinámicamente la enseñanza, ejercicios y evaluaciones, fundamentándose en material oficial chileno.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/49e0bbe4-6ca3-437b-97a2-b968c413073f" />



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

## 📚 Documentación técnica

La documentación completa del proyecto (arquitectura, backend, frontend, base de datos, pipeline RAG, API, flujos y despliegue) está en la carpeta [docs/](./docs/README.md).

## Ejecutar

docker compose up --build

Frontend:
http://localhost:5173

Backend:
http://localhost:8000

Swagger:
http://localhost:8000/docs

## Demo & Preview

Ruta de lecciones
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/211d0dc1-164f-46e0-b358-0a1aca498be8" />

Clases
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a29d845c-923d-40ec-a43b-2154a5c3b58b" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/ff1c1eb5-39dd-4762-a9a4-6c15b4c22ca9" />

Quiz
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1b9b02be-a3af-4c4f-9ab9-ca1b3ac4ccc2" />

ChatBot
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e48033ad-37ac-4d15-8081-52290ab22581" />


## 📄 Licencia y Propiedad Intelectual

Este proyecto ha sido desarrollado de manera conjunta por **Brendan Rubilar Vivanco** y **Tomás Cid Muñoz**. 

El código fuente se encuentra alojado en este repositorio de forma pública únicamente con fines de **evaluación técnica y muestra de arquitectura**. 

Todos los derechos sobre el software, la lógica de negocio y los componentes visuales están reservados. No está permitida su copia, distribución ni utilización sin la autorización expresa de los autores. Consulta el archivo [LICENSE](./LICENSE) para más detalles.
