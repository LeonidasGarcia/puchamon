import App from "./pages/App";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./api/queryClient";

function Layout() {
  return (
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
}

export default Layout;
