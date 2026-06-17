export type AiDifficulty = 1 | 2 | 3 | 4;

export const AI_DIFFICULTY_LABELS: Record<AiDifficulty, string> = {
  1: 'Fácil',
  2: 'Medio',
  3: 'Difícil',
  4: 'GA',
};

export const AI_DIFFICULTY_VALUES: AiDifficulty[] = [1, 2, 3, 4];
