import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConnectionStore } from '../stores/connectionStore';
import { useBattleNetworkStore } from '../stores/battleNetworkStore';
import {
  AI_DIFFICULTY_LABELS,
  AI_DIFFICULTY_VALUES,
} from '../types/difficulty';

export default function Lobby() {
  const navigate = useNavigate();
  const {
    name,
    controllerType,
    difficulty,
    ai2_difficulty,
    battleType,
    setName,
    setControllerType,
    setDifficulty,
    setAi2Difficulty,
    setBattleType,
  } = useConnectionStore();
  const connect = useBattleNetworkStore((state) => state.connect);

  useEffect(() => {
    if (controllerType === null) setControllerType('human');
    if (battleType === null) setBattleType('1v1');
    if (difficulty === null) setDifficulty(1);
    if (ai2_difficulty === null) setAi2Difficulty(1);
  }, []);

  const handleStartBattle = () => {
    if (!name || !controllerType || !difficulty || !battleType) return;
    if (controllerType === 'ai' && !ai2_difficulty) return;

    connect({
      name,
      controller_type: controllerType,
      battle_type: battleType,
      difficulty,
      ai2_difficulty: controllerType === 'ai' ? ai2_difficulty : undefined,
    });
    navigate('/battle');
  };

  const isConfigValid =
    name &&
    controllerType &&
    difficulty &&
    battleType &&
    (controllerType === 'human' || ai2_difficulty);

  return (
    <div className="min-h-screen bg-neutral-900 flex items-center justify-center">
      <div className="bg-neutral-800 rounded-2xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-white text-center mb-8">
          Puchamon
        </h1>

        <div className="flex flex-col gap-6">
          <div>
            <label className="block text-white text-sm mb-2">Nombre</label>
            <input
              type="text"
              value={name ?? ''}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 bg-neutral-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-white text-sm mb-2">
              Modo de Juego
            </label>
            <div className="flex gap-4">
              <button
                onClick={() => setControllerType('human')}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  controllerType === 'human'
                    ? 'bg-blue-600 text-white'
                    : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                }`}
              >
                Human vs AI
              </button>
              <button
                onClick={() => setControllerType('ai')}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  controllerType === 'ai'
                    ? 'bg-blue-600 text-white'
                    : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                }`}
              >
                AI vs AI
              </button>
            </div>
          </div>

          {controllerType === 'human' && (
            <div>
              <label className="block text-white text-sm mb-2">
                Dificultad
              </label>
              <div className="flex gap-4">
                {AI_DIFFICULTY_VALUES.map((d) => (
                  <button
                    key={d}
                    onClick={() => setDifficulty(d)}
                    className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                      difficulty === d
                        ? 'bg-blue-600 text-white'
                        : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                    }`}
                  >
                    {AI_DIFFICULTY_LABELS[d]}
                  </button>
                ))}
              </div>
            </div>
          )}

          {controllerType === 'ai' && (
            <div className="space-y-4">
              <div>
                <label className="block text-white text-sm mb-2">
                  Dificultad IA 1
                </label>
                <div className="flex gap-4">
                  {AI_DIFFICULTY_VALUES.map((d) => (
                    <button
                      key={d}
                      onClick={() => setDifficulty(d)}
                      className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                        difficulty === d
                          ? 'bg-blue-600 text-white'
                          : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                      }`}
                    >
                      {AI_DIFFICULTY_LABELS[d]}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-white text-sm mb-2">
                  Dificultad IA 2
                </label>
                <div className="flex gap-4">
                  {AI_DIFFICULTY_VALUES.map((d) => (
                    <button
                      key={d}
                      onClick={() => setAi2Difficulty(d)}
                      className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                        ai2_difficulty === d
                          ? 'bg-blue-600 text-white'
                          : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                      }`}
                    >
                      {AI_DIFFICULTY_LABELS[d]}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div>
            <label className="block text-white text-sm mb-2">
              Tipo de Batalla
            </label>
            <div className="flex gap-4">
              {(['1v1', '2v2', '3v3'] as const).map((bt) => (
                <button
                  key={bt}
                  onClick={() => setBattleType(bt)}
                  className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                    battleType === bt
                      ? 'bg-blue-600 text-white'
                      : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                  }`}
                >
                  {bt}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleStartBattle}
            disabled={!isConfigValid}
            className={`mt-4 w-full px-6 py-3 font-bold rounded-lg transition-colors ${
              isConfigValid
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-neutral-600 text-neutral-400 cursor-not-allowed'
            }`}
          >
            Iniciar Batalla
          </button>
        </div>
      </div>
    </div>
  );
}
