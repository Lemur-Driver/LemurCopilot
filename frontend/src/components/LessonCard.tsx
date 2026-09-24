import { useNavigate } from 'react-router-dom'
import type { Lesson } from '../data/course'

interface LessonCardProps {
  lesson: Lesson
  number: number
}

function LessonCard({ lesson, number }: LessonCardProps) {
  const navigate = useNavigate()

  return (
    <button
      className="lesson-card"
      onClick={() => navigate(`/lesson/${lesson.id}`)}
    >
      <div className="lesson-number">
        {number}
      </div>

      <div className="lesson-info">
        <span className="lesson-code">{lesson.code}</span>

        <h3>{lesson.title}</h3>

        <p>{lesson.description}</p>
      </div>

      <div className="lesson-arrow">
        →
      </div>
    </button>
  )
}

export default LessonCard