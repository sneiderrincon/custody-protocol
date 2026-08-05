import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const apiTarget = process.env.VITE_API_TARGET ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    // El proxy hace que el navegador llame al mismo origen que sirve la SPA,
    // así el backend no necesita CORS_ALLOWED_ORIGINS para desarrollo local.
    // En produccion este rol lo cumple el reverse-proxy (arquitectura, 8.1).
    proxy: {
      "/v1": { target: apiTarget, changeOrigin: true },
      "/healthz": { target: apiTarget, changeOrigin: true },
    },
  },
});
