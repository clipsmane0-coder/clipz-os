// ============================================================
// CLIPZ — Real API Client (FastAPI backend)
// ============================================================
// Mirrors the mock-client.ts interface but makes actual HTTP
// calls to the FastAPI backend at apiConfig.baseUrl.
// Every function returns snake_case API envelopes matching
// the Technical Specification.
// ============================================================

import { apiConfig } from "./config";
import { getAuthToken } from "../auth/auth-context";

const BASE = apiConfig.baseUrl;

async function request<T>(method: string, path: string, body?: any): Promise<T> {
  const url = `${BASE}${path}`;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await res.json();
  if (!res.ok) throw json;
  return json as T;
}

function params(obj: Record<string, any>): string {
  const parts: string[] = [];
  for (const [k, v] of Object.entries(obj)) {
    if (v !== undefined && v !== null && v !== "") {
      parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`);
    }
  }
  return parts.length ? `?${parts.join("&")}` : "";
}

// === HEALTH ===
export function getHealth() {
  return request<any>("GET", "/health");
}

// === PROFILES ===
export function listProfiles(p: Record<string, any> = {}) {
  return request<any>("GET", `/profiles${params(p)}`);
}
export function getProfile(id: string) {
  return request<any>("GET", `/profiles/${id}`);
}
export function createProfile(data: any) {
  return request<any>("POST", "/profiles", data);
}
export function updateProfile(id: string, data: any) {
  return request<any>("PATCH", `/profiles/${id}`, data);
}
export function deleteProfile(id: string) {
  return request<any>("DELETE", `/profiles/${id}`);
}
export function pauseProfile(id: string) {
  return request<any>("POST", `/profiles/${id}/pause`);
}
export function resumeProfile(id: string) {
  return request<any>("POST", `/profiles/${id}/resume`);
}
export function archiveProfile(id: string) {
  return request<any>("POST", `/profiles/${id}/archive`);
}

// === SOURCES ===
export function listSources(p: Record<string, any> = {}) {
  return request<any>("GET", `/sources${params(p)}`);
}
export function getSource(id: string) {
  return request<any>("GET", `/sources/${id}`);
}
export function createSource(data: any) {
  return request<any>("POST", "/sources", data);
}
export function updateSource(id: string, data: any) {
  return request<any>("PATCH", `/sources/${id}`, data);
}
export function deleteSource(id: string) {
  return request<any>("DELETE", `/sources/${id}`);
}
export function archiveSource(id: string) {
  return request<any>("POST", `/sources/${id}/archive`);
}

// === CANDIDATES ===
export function listCandidates(p: Record<string, any> = {}) {
  return request<any>("GET", `/candidates${params(p)}`);
}
export function getCandidate(id: string) {
  return request<any>("GET", `/candidates/${id}`);
}
export function createCandidate(data: any) {
  return request<any>("POST", "/candidates", data);
}
export function updateCandidate(id: string, data: any) {
  return request<any>("PATCH", `/candidates/${id}`, data);
}
export function approveCandidate(id: string) {
  return request<any>("POST", `/candidates/${id}/approve`);
}
export function rejectCandidate(id: string) {
  return request<any>("POST", `/candidates/${id}/reject`);
}
export function archiveCandidate(id: string) {
  return request<any>("POST", `/candidates/${id}/archive`);
}

// === JOBS ===
export function listJobs(p: Record<string, any> = {}) {
  return request<any>("GET", `/jobs${params(p)}`);
}
export function getJob(id: string) {
  return request<any>("GET", `/jobs/${id}`);
}
export function createJob(data: any) {
  return request<any>("POST", "/jobs", data);
}
export function retryJob(id: string) {
  return request<any>("POST", `/jobs/${id}/retry`);
}
export function cancelJob(id: string) {
  return request<any>("POST", `/jobs/${id}/cancel`);
}
export function pauseJob(id: string) {
  return request<any>("POST", `/jobs/${id}/pause`);
}
export function resumeJob(id: string) {
  return request<any>("POST", `/jobs/${id}/resume`);
}

// === SETTINGS ===
export function getSystemSettings() {
  return request<any>("GET", "/settings");
}
export function updateSystemSetting(key: string, value: string) {
  return request<any>("PATCH", "/settings", { key, value });
}

// === NOTIFICATIONS ===
export function listNotifications(p: Record<string, any> = {}) {
  return request<any>("GET", `/notifications${params(p)}`);
}
export function markNotificationRead(id: string) {
  return request<any>("POST", `/notifications/${id}/read`);
}

// === PROFILE SETTINGS ===
export function getProfileSettings(profileId: string) {
  return request<any>("GET", `/settings/profile/${profileId}`);
}
export function updateProfileSetting(profileId: string, key: string, value: string) {
  return request<any>("PUT", `/settings/profile/${profileId}/${key}`, { key, value });
}

// === SOURCE UPLOAD ===
export async function uploadSource(profileId: string, file: File, title?: string, rightsStatus?: string): Promise<any> {
  const form = new FormData();
  form.append("file", file);
  let url = `${BASE}/sources/upload?profile_id=${encodeURIComponent(profileId)}`;
  if (title) url += `&title=${encodeURIComponent(title)}`;
  if (rightsStatus) url += `&rights_status=${encodeURIComponent(rightsStatus)}`;
  const token = getAuthToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(url, { method: "POST", body: form, headers });
  const json = await res.json();
  if (!res.ok) throw json;
  return json;
}

// === URL REGISTRATION ===
export async function registerSourceUrl(profileId: string, sourceUrl: string, title?: string, platform?: string, rightsStatus?: string): Promise<any> {
  return request<any>("POST", "/sources/register-url", {
    profile_id: profileId,
    source_url: sourceUrl,
    title: title,
    platform: platform,
    rights_status: rightsStatus || "unknown",
  });
}