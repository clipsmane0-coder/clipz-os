// ============================================================
// CLIPZ — API Mode Configuration
// ============================================================
// Controls whether the frontend uses mock data or the real
// FastAPI backend. Set via VITE_API_MODE env var.
//
//   VITE_API_MODE=mock    (default — uses local seed data)
//   VITE_API_MODE=real    (uses FastAPI backend)
//   VITE_API_BASE_URL=http://localhost:8000/api/v1
// ============================================================

export type ApiMode = "mock" | "real";

const mode: ApiMode = "real";
const baseUrl: string = "https://clipz-api-dev.fly.dev/api/v1";

export const apiConfig = {
  mode,
  baseUrl,
  isMock: mode === "mock",
  isReal: mode === "real",
};
