import { useState } from 'react'

export interface QuizQuestion {
  question: string
  options: string[]
  correctAnswer: number
}

interface QuizProps {
  questions: QuizQuestion[]
}

function Quiz({ questions }: QuizProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)

  const question = questions[currentQuestion]

  const isCorrect =
    selectedAnswer !== null &&
    selectedAnswer === question.correctAnswer

  const handleAnswer = (index: number) => {
    if (selectedAnswer !== null) return

    setSelectedAnswer(index)
  }

  const nextQuestion = () => {
    setSelectedAnswer(null)

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  return (
    <section className="quiz">

      <div className="quiz-header">
        <span>Quiz</span>

        <small>
          Pregunta {currentQuestion + 1} de {questions.length}
        </small>
      </div>

      <h2>{question.question}</h2>

      <div className="quiz-options">

        {question.options.map((option, index) => {

          let className = 'quiz-option'

          if (selectedAnswer !== null) {
            if (index === question.correctAnswer) {
              className += ' correct'
            } else if (index === selectedAnswer) {
              className += ' incorrect'
            }
          }

          return (
            <button
              key={index}
              className={className}
              onClick={() => handleAnswer(index)}
            >
              <span>
                {String.fromCharCode(65 + index)}
              </span>

              {option}
            </button>
          )
        })}

      </div>

      {selectedAnswer !== null && (
        <div className="quiz-feedback">

          <p>
            {isCorrect
              ? '🎉 ¡Correcto!'
              : '💡 No exactamente. Revisa la respuesta correcta.'}
          </p>

          {currentQuestion < questions.length - 1 && (
            <button
              className="next-button"
              onClick={nextQuestion}
            >
              Siguiente pregunta →
            </button>
          )}

        </div>
      )}

    </section>
  )
}

export default Quiz