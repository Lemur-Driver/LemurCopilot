import { useState } from 'react'

export interface QuizQuestion {
  question: string
  options: string[]
  correctAnswer: number
}

interface QuizProps {
  questions: QuizQuestion[]
}

function Quiz({
  questions,
}: QuizProps) {

  const [
    currentQuestion,
    setCurrentQuestion,
  ] = useState(0)

  const [
    selectedAnswer,
    setSelectedAnswer,
  ] = useState<number | null>(null)


  const question =
    questions[currentQuestion]


  const isCorrect =
    selectedAnswer !== null &&
    selectedAnswer ===
      question.correctAnswer


  const handleAnswer = (
    index: number
  ) => {

    if (
      selectedAnswer !== null
    ) {
      return
    }

    setSelectedAnswer(index)
  }


  const nextQuestion = () => {

    setSelectedAnswer(null)

    if (
      currentQuestion <
      questions.length - 1
    ) {
      setCurrentQuestion(
        currentQuestion + 1
      )
    }

  }


  const progress =
    ((currentQuestion + 1) /
      questions.length) *
    100


  return (
    <section className="quiz">

      <div className="quiz-header">

        <div>

          <span className="quiz-label">
            🎯 Desafío
          </span>

          <h2>
            Demuestra lo que aprendiste
          </h2>

        </div>


        <div className="quiz-counter">
          {currentQuestion + 1}
          {' / '}
          {questions.length}
        </div>

      </div>


      <div className="quiz-progress">

        <div
          className="quiz-progress-fill"
          style={{
            width: `${progress}%`,
          }}
        />

      </div>


      <div className="quiz-question">

        <span>
          Pregunta {currentQuestion + 1}
        </span>

        <h3>
          {question.question}
        </h3>

      </div>


      <div className="quiz-options">

        {question.options.map(
          (option, index) => {

            let className =
              'quiz-option'

            if (
              selectedAnswer !== null
            ) {

              if (
                index ===
                question.correctAnswer
              ) {

                className +=
                  ' correct'

              } else if (
                index ===
                selectedAnswer
              ) {

                className +=
                  ' incorrect'

              }

            }


            return (
              <button
                key={index}
                className={className}
                onClick={() =>
                  handleAnswer(index)
                }
              >

                <span className="option-letter">
                  {String.fromCharCode(
                    65 + index
                  )}
                </span>


                <span className="option-text">
                  {option}
                </span>

              </button>
            )
          }
        )}

      </div>


      {selectedAnswer !== null && (

        <div
          className={
            isCorrect
              ? 'quiz-feedback correct-feedback'
              : 'quiz-feedback wrong-feedback'
          }
        >

          <div className="feedback-icon">
            {isCorrect
              ? '🎉'
              : '💡'}
          </div>


          <div className="feedback-text">

            <strong>
              {isCorrect
                ? '¡Muy bien!'
                : 'Casi lo tienes'}
            </strong>

            <p>
              {isCorrect
                ? 'Esa es la respuesta correcta.'
                : 'La respuesta correcta está marcada en verde.'}
            </p>

          </div>


          {currentQuestion <
            questions.length - 1 && (

            <button
              className="next-button"
              onClick={nextQuestion}
            >
              Continuar
              <span>→</span>
            </button>

          )}

        </div>

      )}

    </section>
  )
}

export default Quiz