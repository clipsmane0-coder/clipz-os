// ============================================================
// CLIPZ — API Client (mode-switching layer)
// ============================================================
// Default: mock mode (local seed data).
// Set VITE_API_MODE=real and VITE_API_BASE_URL for FastAPI.
// ============================================================

import { apiConfig } from "./config";

if (apiConfig.isReal) {
  console.log("CLIPZ API: real mode —", apiConfig.baseUrl);
}

// Export the full mock client — it works in both modes.
// In real mode, individual hooks can be swapped to the
// real client when the backend is deployed.
export * from "./mock-client";