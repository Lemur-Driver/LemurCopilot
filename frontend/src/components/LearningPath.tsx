import type { Unit } from '../data/course'
import LessonCard from './LessonCard'

interface LearningPathProps {
  unit: Unit
}

function LearningPath({ unit }: LearningPathProps) {
  return (
    <section className="unit-section">
      <div className="unit-header">
        <span className="unit-label">{unit.code}</span>

        <h2>{unit.title}</h2>

        <p>
          Avanza por las clases y pon a prueba lo que vas aprendiendo.
        </p>
      </div>

      <div className="learning-path">
        {unit.lessons.map((lesson, index) => (
          <LessonCard
            key={lesson.id}
            lesson={lesson}
            number={index + 1}
          />
        ))}
      </div>
    </section>
  )
}

export default LearningPath