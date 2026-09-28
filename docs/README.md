# 📚 Documentación Técnica — LemurCopilot

**Sistema de tutoría adaptativa para la preparación del examen teórico de licencia de conducir Clase B (Chile).**

LemurCopilot es una plataforma de aprendizaje que combina un modelo del conocimiento del estudiante con un agente de IA para generar dinámicamente lecciones, quizzes y tutorías conversacionales, todo fundamentado en el manual oficial de conducción chileno (CONASET).

---

## 🗂️ Índice de la documentación

| # | Documento | Contenido |
|---|-----------|-----------|
| 01 | [Arquitectura del sistema](./01-arquitectura.md) | Visión general, diagrama de componentes, stack tecnológico y decisiones de diseño. |
| 02 | [Backend (FastAPI)](./02-backend.md) | Estructura del servidor, capas (rutas / servicios / prompts), responsabilidad de cada módulo. |
| 03 | [Frontend (React)](./03-frontend.md) | Páginas, componentes, enrutamiento, consumo de la API y streaming. |
| 04 | [Base de datos (MongoDB)](./04-base-de-datos.md) | Colecciones, esquemas de documentos, índices y búsqueda vectorial. |
| 05 | [Pipeline RAG](./05-pipeline-rag.md) | Ingesta del manual, chunking, embeddings, recuperación y guardrails del tutor. |
| 06 | [Referencia de API REST](./06-api-rest.md) | Todos los endpoints: contratos de request/response y ejemplos. |
| 07 | [Flujos end-to-end](./07-flujos-end-to-end.md) | Diagramas de secuencia de los flujos principales del sistema. |
| 08 | [Despliegue y configuración](./08-despliegue-y-configuracion.md) | Docker Compose, variables de entorno y ejecución local. |

---

## ⚡ Lectura rápida (5 minutos)

Si solo quieres entender **qué hace el sistema y cómo se conecta**, lee en este orden:

1. [Arquitectura del sistema](./01-arquitectura.md) → el mapa general.
2. [Flujos end-to-end](./07-flujos-end-to-end.md) → cómo viaja una petición por todo el sistema.
3. [Despliegue](./08-despliegue-y-configuracion.md) → cómo levantarlo.

## 🧭 Guía según tu rol

| Si eres... | Empieza por... |
|------------|----------------|
| Desarrollador backend nuevo | [02 - Backend](./02-backend.md) → [05 - Pipeline RAG](./05-pipeline-rag.md) → [06 - API](./06-api-rest.md) |
| Desarrollador frontend nuevo | [03 - Frontend](./03-frontend.md) → [06 - API](./06-api-rest.md) |
| DevOps / infraestructura | [08 - Despliegue](./08-despliegue-y-configuracion.md) → [04 - Base de datos](./04-base-de-datos.md) |
| Revisor técnico / evaluador | [01 - Arquitectura](./01-arquitectura.md) → [07 - Flujos](./07-flujos-end-to-end.md) |

---

## 🔧 Stack en una línea

> **React 19 + TypeScript + Vite** ⇄ **FastAPI (Python 3.12)** ⇄ **MongoDB Atlas (Vector Search)** + **Sentence Transformers** + **Ollama / Google Gemini**, todo orquestado con **Docker Compose**.

## 👥 Autoría

Desarrollado por **Brendan Rubilar Vivanco** y **Tomás Cid Muñoz**. Código publicado con fines de evaluación técnica; ver [LICENSE](../LICENSE).
