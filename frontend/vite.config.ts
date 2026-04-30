import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/poke-gifs": {
        target: "https://img.pokemondb.net",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/poke-gifs/, ""),
      },
      "/mini-poke-sprites": {
        target: "https://raw.githubusercontent.com",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/mini-poke-sprites/, ""),
      },
    },
  },
});
