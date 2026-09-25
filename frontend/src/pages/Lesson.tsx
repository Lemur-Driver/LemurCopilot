import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import Quiz, {
  type QuizQuestion,
} from '../components/Quiz'

import LemurLoader from '../components/LemurLoader'
import { course } from '../data/course'


// ============================================================
// TYPES
// ============================================================

interface GeneratedSection {
  title: string
  content: string
  example?: string
}

interface GeneratedLesson {
  title: string
  introduction: string
  sections: GeneratedSection[]
  key_points: string[]
}

interface LessonSource {
  page: number
  title: string
  source: string
}

interface GenerateLessonResponse {
  topic: string

  lesson: GeneratedLesson

  quiz: {
    questions: QuizQuestion[]
  }

  sources: LessonSource[]
}


// ============================================================
// API
// ============================================================

const API_URL =
  import.meta.env.VITE_API_URL ??
  'http://localhost:8000'


// ============================================================
// COMPONENT
// ============================================================

function Lesson() {
  const { lessonId } = useParams()

  const navigate = useNavigate()


  // ----------------------------------------------------------
  // Información estática de course.ts
  // ----------------------------------------------------------

  const courseLesson = course
    .flatMap(
      (unit) => unit.lessons
    )
    .find(
      (lesson) =>
        lesson.id === lessonId
    )


  // ----------------------------------------------------------
  // State
  // ----------------------------------------------------------

  const [
    generatedContent,
    setGeneratedContent,
  ] = useState<GenerateLessonResponse | null>(
    null
  )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )

  const [
    showQuiz,
    setShowQuiz,
  ] = useState(false)


  // ----------------------------------------------------------
  // Cargar / generar lección
  // ----------------------------------------------------------

  useEffect(() => {
    if (!lessonId) {
      return
    }


    const controller =
      new AbortController()

    let active = true


    const loadLesson = async () => {
      try {
        setLoading(true)
        setError(null)
        setGeneratedContent(null)
        setShowQuiz(false)


        const response = await fetch(
          `${API_URL}/lessons/generate/${encodeURIComponent(
            lessonId
          )}`,
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json',
            },

            signal:
              controller.signal,
          }
        )


        if (!response.ok) {
          const errorData =
            await response
              .json()
              .catch(() => null)

          throw new Error(
            errorData?.detail ??
              `Error ${response.status}`
          )
        }


        const data:
          GenerateLessonResponse =
          await response.json()


        if (!active) {
          return
        }


        setGeneratedContent(
          data
        )

      } catch (error) {

        if (
          error instanceof DOMException &&
          error.name === 'AbortError'
        ) {
          return
        }


        if (!active) {
          return
        }


        console.error(
          'Error cargando lección:',
          error
        )


        setError(
          error instanceof Error
            ? error.message
            : 'No se pudo generar la lección.'
        )

      } finally {

        if (active) {
          setLoading(false)
        }

      }
    }


    loadLesson()


    return () => {
      active = false

      controller.abort()
    }

  }, [lessonId])


  // ==========================================================
  // LECCIÓN NO ENCONTRADA
  // ==========================================================

  if (!courseLesson) {
    return (
      <main className="not-found">

        <div className="not-found-icon">
          🚧
        </div>

        <h1>
          Clase no encontrada
        </h1>

        <p>
          Esta clase todavía no está disponible.
        </p>

        <button
          className="primary-button"
          onClick={() =>
            navigate('/')
          }
        >
          Volver al inicio
        </button>

      </main>
    )
  }


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {
    return (
      <main className="lesson-page">

        <nav className="lesson-nav">

          <button
            className="back-button"
            onClick={() =>
              navigate('/')
            }
            aria-label="Volver al camino"
          >
            ←
          </button>


          <div className="lesson-nav-info">

            <span>
              {courseLesson.code}
            </span>

            <strong>
              Preparando tu clase
            </strong>

          </div>

        </nav>


        <section className="lesson-loading">

          <LemurLoader />

          <h2>
            Preparando tu clase...
          </h2>

          <p>
            El lemur está recorriendo el manual
            y preparando una lección para ti.
          </p>

        </section>

      </main>
    )
  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {
    return (
      <main className="lesson-page">

        <nav className="lesson-nav">

          <button
            className="back-button"
            onClick={() =>
              navigate('/')
            }
            aria-label="Volver al camino"
          >
            ←
          </button>


          <div className="lesson-nav-info">

            <span>
              {courseLesson.code}
            </span>

            <strong>
              Volver al camino
            </strong>

          </div>

        </nav>


        <section className="lesson-error">

          <h2>
            No pudimos generar la clase
          </h2>

          <p>
            {error}
          </p>

          <button
            className="next-button"
            onClick={() =>
              window.location.reload()
            }
          >
            Intentar nuevamente
          </button>

        </section>

      </main>
    )
  }


  // ==========================================================
  // PROTECCIÓN
  // ==========================================================

  if (!generatedContent) {
    return (
      <main className="lesson-page">

        <section className="lesson-error">

          <h2>
            No encontramos el contenido
          </h2>

          <p>
            La clase terminó de cargar,
            pero no recibimos contenido.
          </p>

          <button
            className="next-button"
            onClick={() =>
              window.location.reload()
            }
          >
            Intentar nuevamente
          </button>

        </section>

      </main>
    )
  }


  // ==========================================================
  // QUIZ
  // ==========================================================

  if (showQuiz) {
    return (
      <main className="lesson-page">

        <nav className="lesson-nav">

          <button
            className="back-button"
            onClick={() =>
              setShowQuiz(false)
            }
            aria-label="Volver a la clase"
          >
            ←
          </button>


          <div className="lesson-nav-info">

            <span>
              {courseLesson.code}
            </span>

            <strong>
              Volver a la clase
            </strong>

          </div>

        </nav>


        <header className="lesson-header">

          <div className="lesson-header-label">
            QUIZ
          </div>


          <h1>
            {courseLesson.title}
          </h1>


          <p>
            Pon a prueba lo que acabas
            de aprender.
          </p>

        </header>


        <Quiz
          questions={
            generatedContent
              .quiz
              .questions
          }
        />

      </main>
    )
  }


  // ==========================================================
  // LECCIÓN
  // ==========================================================

  return (
    <main className="lesson-page">

      <nav className="lesson-nav">

        <button
          className="back-button"
          onClick={() =>
            navigate('/')
          }
          aria-label="Volver al camino"
        >
          ←
        </button>


        <div className="lesson-nav-info">

          <span>
            {courseLesson.code}
          </span>

          <strong>
            Volver al camino
          </strong>

        </div>

      </nav>


      {/* ================================================== */}
      {/* HEADER                                             */}
      {/* ================================================== */}

      <header className="lesson-header">

        <div className="lesson-header-label">
          {courseLesson.code}
        </div>


        <h1>
          {courseLesson.title}
        </h1>


        <p>
          {courseLesson.description}
        </p>

      </header>


      {/* ================================================== */}
      {/* CONTENIDO GENERADO                                 */}
      {/* ================================================== */}

      <section className="lesson-content">

        <div className="content-label">
          MINI CLASE
        </div>


        <h2>
          {
            generatedContent
              .lesson
              .title
          }
        </h2>


        <p className="lesson-introduction">
          {
            generatedContent
              .lesson
              .introduction
          }
        </p>


        {/* ================================================ */}
        {/* SECCIONES                                        */}
        {/* ================================================ */}

        <div className="lesson-sections">

          {generatedContent
            .lesson
            .sections
            .map(
              (
                section,
                index
              ) => (
                <article
                  className="lesson-section"
                  key={index}
                >

                  <h3>
                    {section.title}
                  </h3>


                  <p>
                    {section.content}
                  </p>


                  {section.example && (
                    <div className="lesson-example">

                      <strong>
                        💡 Ejemplo
                      </strong>

                      <p>
                        {section.example}
                      </p>

                    </div>
                  )}

                </article>
              )
            )}

        </div>


        {/* ================================================ */}
        {/* PUNTOS CLAVE                                     */}
        {/* ================================================ */}

        {generatedContent
          .lesson
          .key_points
          .length > 0 && (
          <div className="lesson-key-points">

            <h3>
              Recuerda
            </h3>


            <ul>

              {generatedContent
                .lesson
                .key_points
                .map(
                  (
                    point,
                    index
                  ) => (
                    <li key={index}>
                      {point}
                    </li>
                  )
                )}

            </ul>

          </div>
        )}


        {/* ================================================ */}
        {/* FUENTES                                          */}
        {/* ================================================ */}

        {generatedContent
          .sources
          .length > 0 && (
          <div className="lesson-sources">

            <small>

              📚 Basado en el Libro para la
              Conducción en Chile · páginas{' '}

              {generatedContent
                .sources
                .map(
                  (source) =>
                    source.page
                )
                .join(', ')}

            </small>

          </div>
        )}


        {/* ================================================ */}
        {/* IR AL QUIZ                                       */}
        {/* ================================================ */}

        <div className="lesson-actions">

          <button
            className="start-quiz-button"
            onClick={() => {
              window.scrollTo({
                top: 0,
                behavior: 'smooth',
              })

              setShowQuiz(true)
            }}
          >
            Comenzar quiz →
          </button>

        </div>

      </section>

    </main>
  )
}


export default Lesson