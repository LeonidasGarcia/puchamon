import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './api/queryClient';
import Lobby from './pages/Lobby';
import App from './pages/App';
import Playground from './pages/Playground';
import BattleGuard from './components/guards/BattleGuard';

function Layout() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Lobby />} />
          <Route
            path="/battle"
            element={
              <BattleGuard>
                <App />
              </BattleGuard>
            }
          />
          <Route path="/playground" element={<Playground />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default Layout;
