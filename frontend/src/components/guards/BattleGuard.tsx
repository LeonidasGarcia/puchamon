import { useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useConnectionStore } from '../../stores/connectionStore';

export default function BattleGuard({ children }: { children: React.ReactNode }) {
  const name = useConnectionStore((state) => state.name);
  const navigate = useNavigate();

  useEffect(() => {
    if (name === null) {
      navigate('/', { replace: true });
    }
  }, [name, navigate]);

  if (name === null) {
    return null;
  }

  return <>{children}</>;
}