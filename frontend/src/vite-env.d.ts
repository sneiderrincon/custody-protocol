/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Credenciales del usuario de demostracion (ver src/auth/DemoSessionProvider.ts). */
  readonly VITE_DEMO_EMAIL?: string;
  readonly VITE_DEMO_PASSWORD?: string;
  readonly VITE_DEMO_ACTOR_ID?: string;
  /**
   * JWT emitido por generar_token.py (raiz del repo) para hablar con FastAPI
   * sin BFF. Ver frontend/.env.example.
   * Solo para demos locales: queda embebido en el bundle del navegador.
   */
  readonly VITE_DEMO_JWT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
