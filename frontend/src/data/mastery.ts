export interface MasteryEntry {
  score: number
  last_score: number
  best_score: number
  attempts: number
  last_seen: string | null
  failed_questions: string[]
}

export type MasteryMap = Record<string, MasteryEntry>
