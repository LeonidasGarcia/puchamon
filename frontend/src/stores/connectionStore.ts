import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ConnectionState {
  name: string | null;
  controllerType: 'human' | 'ai' | null;
  difficulty: 1 | 2 | 3 | null;
  ai2_difficulty: 1 | 2 | 3 | null;
  battleType: '1v1' | '2v2' | '3v3' | null;
  setName: (name: string) => void;
  setControllerType: (type: 'human' | 'ai') => void;
  setDifficulty: (difficulty: 1 | 2 | 3) => void;
  setAi2Difficulty: (difficulty: 1 | 2 | 3) => void;
  setBattleType: (type: '1v1' | '2v2' | '3v3') => void;
  reset: () => void;
}

export const useConnectionStore = create<ConnectionState>()(
  persist(
    (set) => ({
      name: null,
      controllerType: null,
      difficulty: null,
      ai2_difficulty: null,
      battleType: null,
      setName: (name) => set({ name }),
      setControllerType: (controllerType) => set({ controllerType }),
      setDifficulty: (difficulty) => set({ difficulty }),
      setAi2Difficulty: (ai2_difficulty) => set({ ai2_difficulty }),
      setBattleType: (battleType) => set({ battleType }),
      reset: () =>
        set({
          name: null,
          controllerType: null,
          difficulty: null,
          ai2_difficulty: null,
          battleType: null,
        }),
    }),
    {
      name: 'puchamon-connection',
    },
  ),
);
