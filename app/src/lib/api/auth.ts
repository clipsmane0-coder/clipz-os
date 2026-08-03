// ============================================================
// CLIPZ — Auth API Client
// ============================================================

import { apiConfig } from "./config";

const BASE = apiConfig.baseUrl;

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  token: string;
  user: AuthUser;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  meta: { request_id: string };
}

async function request<T>(method: string, path: string, body?: any, token?: string): Promise<T> {
  const url = `${BASE}${path}`;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await res.json();
  if (!res.ok) {
    throw json;
  }
  return json as T;
}

export function register(email: string, password: string, displayName: string) {
  return request<ApiEnvelope<LoginResponse>>("POST", "/auth/register", {
    email,
    password,
    display_name: displayName,
  });
}

export function login(email: string, password: string) {
  return request<ApiEnvelope<LoginResponse>>("POST", "/auth/login", {
    email,
    password,
  });
}

export function logout(token: string) {
  return request<ApiEnvelope<{ message: string }>>("POST", "/auth/logout", undefined, token);
}

export function getMe(token: string) {
  return request<ApiEnvelope<AuthUser>>("GET", "/auth/me", undefined, token);
}