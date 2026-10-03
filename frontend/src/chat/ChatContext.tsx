import {
  createContext,
  useState,
  type ReactNode,
} from 'react'


// ============================================================
// TYPES
// ============================================================

export interface LessonChatContext {
  title: string
  introduction: string

  sections: {
    title: string
    content: string
    example?: string
  }[]

  key_points: string[]
}


export interface QuizExplanationRequest {
  topic: string
  exerciseId: string
  selectedIndex: number
  lesson: LessonChatContext
}


interface ChatContextValue {
  isOpen: boolean

  pendingExplanation:
    QuizExplanationRequest | null

  openChat: () => void

  closeChat: () => void

  toggleChat: () => void

  explainQuizMistake: (
    request: QuizExplanationRequest
  ) => void

  consumeExplanation: () => void
}


// ============================================================
// CONTEXT
// ============================================================

export const ChatContext =
  createContext<ChatContextValue | null>(
    null
  )


// ============================================================
// PROVIDER
// ============================================================

interface ChatProviderProps {
  children: ReactNode
}


export function ChatProvider({
  children,
}: ChatProviderProps) {

  const [
    isOpen,
    setIsOpen,
  ] = useState(false)


  const [
    pendingExplanation,
    setPendingExplanation,
  ] =
    useState<QuizExplanationRequest | null>(
      null
    )


  const openChat = () => {
    setIsOpen(true)
  }


  const closeChat = () => {
    setIsOpen(false)
  }


  const toggleChat = () => {
    setIsOpen(
      (current) => !current
    )
  }


  const explainQuizMistake = (
    request: QuizExplanationRequest
  ) => {

    setPendingExplanation(request)

    setIsOpen(true)
  }


  const consumeExplanation = () => {
    setPendingExplanation(null)
  }


  return (
    <ChatContext.Provider
      value={{
        isOpen,
        pendingExplanation,
        openChat,
        closeChat,
        toggleChat,
        explainQuizMistake,
        consumeExplanation,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}