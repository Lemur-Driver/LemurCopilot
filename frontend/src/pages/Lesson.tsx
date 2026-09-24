import { useNavigate, useParams } from 'react-router-dom'
import Quiz, { type QuizQuestion } from '../components/Quiz'
import LemurLoader from '../components/LemurLoader'
import { course } from '../data/course'

const mockQuestions: QuizQuestion[] = [
  {
    question:
      '¿Cuál de los siguientes factores tiene una incidencia importante en la ocurrencia de siniestros de tránsito?',
    options: [
      'La imprudencia de quien conduce',
      'El color del vehículo',
      'La marca del automóvil',
      'La cantidad de pasajeros',
    ],
    correctAnswer: 0,
  },
  {
    question:
      '¿Cuál es uno de los objetivos del enfoque de Sistema Seguro?',
    options: [
      'Eliminar completamente la conducción humana',
      'Evitar que los errores humanos tengan consecuencias graves',
      'Aumentar la velocidad promedio',
      'Reducir el número de vehículos nuevos',
    ],
    correctAnswer: 1,
  },
  {
    question:
      '¿Qué reconoce el enfoque de Sistema Seguro respecto a las personas?',
    options: [
      'Que nunca cometen errores',
      'Que solamente los conductores experimentados cometen errores',
      'Que los seres humanos pueden cometer errores',
      'Que los errores no influyen en los siniestros',
    ],
    correctAnswer: 2,
  },
]

function Lesson() {
  const { lessonId } = useParams()
  const navigate = useNavigate()

  const lesson = course
    .flatMap((unit) => unit.lessons)
    .find((lesson) => lesson.id === lessonId)

  if (!lesson) {
    return (
      <main className="not-found">
        <h1>Clase no encontrada</h1>

        <button onClick={() => navigate('/')}>
          Volver al inicio
        </button>
      </main>
    )
  }

  return (
    <main className="lesson-page">

      <button
        className="back-button"
        onClick={() => navigate('/')}
      >
        ← Volver al camino
      </button>

      <header className="lesson-header">

        <span>{lesson.code}</span>

        <h1>{lesson.title}</h1>

        <p>{lesson.description}</p>

      </header>

      <section className="lesson-content">

        <div className="lesson-content-label">
          📖 Mini clase
        </div>

        <h2>
          Aprende lo esencial
        </h2>

        <p>
          En esta clase aprenderás los conceptos fundamentales
          relacionados con los siniestros de tránsito en Chile.
        </p>

        <p>
          Este contenido será generado dinámicamente utilizando
          el manual oficial y nuestro sistema RAG.
        </p>

      </section>

      <LemurLoader />

      <Quiz questions={mockQuestions} />

    </main>
  )
}

export default Lesson