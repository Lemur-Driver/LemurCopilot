import type { Unit } from '../data/course'
import LessonCard from './LessonCard'

interface LearningPathProps {
  unit: Unit
}

function LearningPath({
  unit,
}: LearningPathProps) {

  return (
    <section className="unit-section">

      <div className="unit-header">

        <div className="unit-heading">

          <span className="unit-label">
            {unit.code}
          </span>


          <div>

            <h2>
              {unit.title}
            </h2>

            <p>
              Completa cada parada del camino.
            </p>

          </div>

        </div>


        <div className="unit-progress">

          <div className="unit-progress-info">

            <span>
              Progreso
            </span>

            <strong>
              0%
            </strong>

          </div>


          <div className="unit-progress-track">

            <div
              className="unit-progress-fill"
              style={{
                width: '0%',
              }}
            />

          </div>

        </div>

      </div>


      <div className="learning-path">

        {unit.lessons.map(
          (lesson, index) => (

            <LessonCard
              key={lesson.id}
              lesson={lesson}
              number={index + 1}
            />

          )
        )}

      </div>

    </section>
  )
}

export default LearningPath