import { Navigate } from 'react-router-dom';
import { useConnectionStore } from '../../stores/connectionStore';

export default function BattleGuard({ children }: { children: React.ReactNode }) {
  const name = useConnectionStore((state) => state.name);

  if (name === null) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}