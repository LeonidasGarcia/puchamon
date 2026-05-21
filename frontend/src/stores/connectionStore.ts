import { create } from 'zustand';

interface ConnectionState {
  name: string;
  controllerType: 'human' | 'ai';
  difficulty: 1 | 2 | 3;
  battleType: '1v1' | '2v2' | '3v3';
  setName: (name: string) => void;
  setControllerType: (type: 'human' | 'ai') => void;
  setDifficulty: (difficulty: 1 | 2 | 3) => void;
  setBattleType: (type: '1v1' | '2v2' | '3v3') => void;
  reset: () => void;
}

const initialState = {
  name: 'Player',
  controllerType: 'human' as const,
  difficulty: 1 as const,
  battleType: '1v1' as const,
};

export const useConnectionStore = create<ConnectionState>((set) => ({
  ...initialState,
  setName: (name) => set({ name }),
  setControllerType: (controllerType) => set({ controllerType }),
  setDifficulty: (difficulty) => set({ difficulty }),
  setBattleType: (battleType) => set({ battleType }),
  reset: () => set(initialState),
}));
