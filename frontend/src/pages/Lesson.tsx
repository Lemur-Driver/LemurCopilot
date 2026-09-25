import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import Quiz, {
  type QuizQuestion,
} from '../components/Quiz'

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

  const { lessonId } =
    useParams()

  const navigate =
    useNavigate()


  const lesson = course
    .flatMap(
      (unit) => unit.lessons
    )
    .find(
      (lesson) =>
        lesson.id === lessonId
    )


  if (!lesson) {

    return (
      <main className="not-found">

        <div className="not-found-icon">
          🐒
        </div>

        <h1>
          No encontré esta clase
        </h1>

        <p>
          Volvamos al camino.
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


  return (
    <main className="lesson-page">

      <nav className="lesson-nav">

        <button
          className="back-button"
          onClick={() =>
            navigate('/')
          }
        >
          ←
        </button>


        <div className="lesson-nav-info">

          <span>
            {lesson.code}
          </span>

          <strong>
            {lesson.title}
          </strong>

        </div>


        <div className="lesson-nav-xp">
          ⭐ +30 XP
        </div>

      </nav>


      <header className="lesson-header">

        <span className="lesson-header-label">
          📖 LECCIÓN
        </span>


        <h1>
          {lesson.title}
        </h1>


        <p>
          {lesson.description}
        </p>


        <div className="lesson-details">

          <span>
            ⏱ 5–10 min
          </span>

          <span>
            🎯 3 preguntas
          </span>

          <span>
            🇨🇱 Clase B
          </span>

        </div>

      </header>


      <section className="lesson-content">

        <span className="content-label">
          Lo importante
        </span>

        <h2>
          Aprende lo esencial
        </h2>


        <p>
          En esta clase aprenderás
          conceptos fundamentales
          relacionados con los
          siniestros de tránsito
          en Chile.
        </p>


        <div className="tip-card">

          <div className="tip-icon">
            💡
          </div>


          <div>

            <strong>
              Consejo de Lemur
            </strong>

            <p>
              No intentes memorizar.
              Primero comprende la idea
              y luego ponla en práctica.
            </p>

          </div>

        </div>


        <p>
          Este contenido será generado
          dinámicamente utilizando
          el manual oficial y el sistema RAG.
        </p>

      </section>


      <LemurLoader />


      <Quiz
        questions={mockQuestions}
      />

    </main>
  )
}

export default Lesson