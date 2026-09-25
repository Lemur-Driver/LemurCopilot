import { useNavigate } from 'react-router-dom'
import type { Lesson } from '../data/course'

interface LessonCardProps {
  lesson: Lesson
  number: number
}

function LessonCard({
  lesson,
  number,
}: LessonCardProps) {

  const navigate = useNavigate()

  return (
    <button
      className="lesson-card"
      onClick={() =>
        navigate(
          `/lesson/${lesson.id}`
        )
      }
    >

      <div className="lesson-node">

        <span className="lesson-node-number">
          {number}
        </span>

      </div>


      <div className="lesson-info">

        <div className="lesson-meta">

          <span className="lesson-code">
            {lesson.code}
          </span>

          <span className="lesson-duration">
            ⏱ 5–10 min
          </span>

        </div>


        <h3>
          {lesson.title}
        </h3>


        <p>
          {lesson.description}
        </p>

      </div>


      <div className="lesson-action">

        <span>
          Aprender
        </span>

        <div className="lesson-arrow">
          →
        </div>

      </div>

    </button>
  )
}

export default LessonCard