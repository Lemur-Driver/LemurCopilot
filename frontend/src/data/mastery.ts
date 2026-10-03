export interface MasteryEntry {
  score: number
  last_score: number
  best_score: number
  attempts: number
  last_seen: string | null
  failed_questions: string[]
}

export type MasteryMap = Record<string, MasteryEntry>

export interface DashboardSummary {
  total_lessons: number
  completed_lessons: number
  attempted_lessons: number
  total_attempts: number
  preparation: number
  current_streak_days: number
  longest_streak_days: number
  xp: number
}

export interface UnitProgress {
  unit_id: string
  unlocked: boolean
  completed: boolean
  completed_lessons: number
  total_lessons: number
}

export interface CourseProgressResponse {
  units: UnitProgress[]
}