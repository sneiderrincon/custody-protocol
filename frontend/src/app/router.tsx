import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppShell } from "../layouts/AppShell";
import { RequireSession } from "./RequireSession";
import { LoginPage } from "../pages/LoginPage";
import { TrazabilidadPage } from "../pages/TrazabilidadPage";
import { CatalogoPage } from "../pages/CatalogoPage";
import { DeclararPage } from "../pages/DeclararPage";
import { ComingSoonPage } from "../pages/ComingSoonPage";

/**
 * Modulos sin respaldo en el backend. Se declaran aqui, con el endpoint que
 * les falta, para que la razon sea explicita y no una promesa vaga
 * (arquitectura, seccion 4).
 */
const pendingModules = [
  {
    path: "inventario",
    title: "Inventario de dispositivos",
    reason:
      "El catálogo solo permite consultar un dispositivo por identificador exacto. Listar el inventario requiere un endpoint de búsqueda paginada que el backend todavía no expone.",
    missingEndpoint: "GET /v1/catalog/devices (listado paginado)",
  },
  {
    path: "cargas",
    title: "Cargas masivas",
    reason:
      "La importación de aserciones por CSV depende de un endpoint de ingesta masiva que aún no existe en el backend.",
    missingEndpoint: "POST /v1/custody/assertions:bulk",
  },
  {
    path: "auditoria",
    title: "Auditoría",
    reason:
      "El backend registra los rechazos por regla de dominio, pero no expone ninguna ruta HTTP para leer ese log.",
    missingEndpoint: "GET /v1/audit/rejections",
  },
  {
    path: "uso-clinico",
    title: "Uso clínico",
    reason:
      "El evento UsadoImplantado ya existe en el protocolo, pero la vinculación con episodios clínicos y pacientes no está modelada en el backend.",
  },
  {
    path: "calidad",
    title: "Calidad y regulatorio",
    reason:
      "Los retiros de producto (recalls) y los flujos de no conformidad no tienen todavía representación en el dominio.",
    missingEndpoint: "POST /v1/quality/recalls",
  },
];

export const router = createBrowserRouter([
  { path: "/", element: <Navigate to="/app/trazabilidad" replace /> },
  { path: "/login", element: <LoginPage /> },
  {
    element: <RequireSession />,
    children: [
      {
        path: "/app",
        element: <AppShell />,
        children: [
          { index: true, element: <Navigate to="/app/trazabilidad" replace /> },
          { path: "trazabilidad", element: <TrazabilidadPage /> },
          { path: "catalogo", element: <CatalogoPage /> },
          { path: "declarar", element: <DeclararPage /> },
          ...pendingModules.map(({ path, ...props }) => ({
            path,
            element: <ComingSoonPage {...props} />,
          })),
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/app/trazabilidad" replace /> },
]);
