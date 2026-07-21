// ============================================================
// CLIPZ — Mock API Client
// ============================================================
// Simulates the real /api/v1 REST API using local mock data.
// All response formats match the technical spec (snake_case,
// envelope format with meta).
//
// Frontend should NOT import this directly — use the
// TanStack Query hooks in lib/api/hooks.ts instead.
// ============================================================

import * as seed from "./mock-seed";
import type {
  ApiResponse,
  PaginatedResponse,
  ApiErrorResponse,
  DashboardOverview,
  Profile,
  Source,
  Candidate,
  Job,
  Schedule,
  AnalyticsPoint,
  HookTypeStat,
  ClipLengthStat,
  ProfilePerformance,
  Notification,
  Transcript,
  TranscriptSegment,
  Scene,
  CandidateScore,
  CandidateEdit,
  RenderOutput,
  BrandingPreset,
  CaptionPreset,
  RenderPreset,
  ScoringPreset,
} from "../types/clipz";

// ============================================================
// Helpers
// ============================================================

let requestCounter = 0;
const genRequestId = () => `req_${++requestCounter}_${Date.now().toString(36)}`;

function successResponse<T>(data: T): ApiResponse<T> {
  return { success: true, data, meta: { request_id: genRequestId() } };
}

function paginatedResponse<T>(data: T[], page: number, pageSize: number): PaginatedResponse<T> {
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  return {
    success: true,
    data: data.slice(start, end),
    meta: {
      page,
      page_size: pageSize,
      total: data.length,
      request_id: genRequestId(),
    },
  };
}

function errorResponse(code: string, message: string, retryable = false): ApiErrorResponse {
  return {
    success: false,
    error: { code, message, details: {}, retryable },
    meta: { request_id: genRequestId() },
  };
}

// Simulate realistic network latency
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));
const LATENCY_MIN = 80;
const LATENCY_MAX = 250;
const latency = () => delay(LATENCY_MIN + Math.random() * (LATENCY_MAX - LATENCY_MIN));

// ============================================================
// HEALTH
// ============================================================

export async function getHealth() {
  await latency();
  return successResponse({
    api: true,
    database: true,
    worker: true,
    ffmpeg: true,
    transcription: true,
    storage: true,
    version: "0.1.0-mock",
  });
}

// ============================================================
// DASHBOARD
// ============================================================

export async function getDashboardOverview() {
  await latency();
  return successResponse(seed.dashboardOverview as DashboardOverview);
}

// ============================================================
// PROFILES
// ============================================================

export async function listProfiles(params: { page?: number; page_size?: number; status?: string; type?: string } = {}) {
  await latency();
  let data = [...seed.profiles];
  if (params.status) data = data.filter((p) => p.status === params.status);
  if (params.type) data = data.filter((p) => p.profile_type === params.type);
  const page = params.page || 1;
  const pageSize = params.page_size || 25;
  return paginatedResponse(data as Profile[], page, pageSize);
}

export async function getProfile(id: string) {
  await latency();
  const profile = seed.profiles.find((p) => p.id === id);
  if (!profile) throw errorResponse("PROFILE_NOT_FOUND", "The requested profile does not exist.");
  return successResponse(profile as Profile);
}

export async function getProfilePlatforms(profileId: string) {
  await latency();
  const platforms = seed.profilePlatforms.filter((p) => p.profile_id === profileId);
  return successResponse(platforms);
}

export async function getProfileSources(profileId: string) {
  await latency();
  const sources = seed.profileSources.filter((p) => p.profile_id === profileId);
  return successResponse(sources);
}

// ============================================================
// SOURCES
// ============================================================

export async function listSources(params: { page?: number; page_size?: number; status?: string; profile_id?: string } = {}) {
  await latency();
  let data = [...seed.sources];
  if (params.status) data = data.filter((s) => s.status === params.status);
  if (params.profile_id) data = data.filter((s) => s.profile_id === params.profile_id);
  const page = params.page || 1;
  const pageSize = params.page_size || 25;
  return paginatedResponse(data as Source[], page, pageSize);
}

export async function getSource(id: string) {
  await latency();
  const source = seed.sources.find((s) => s.id === id);
  if (!source) throw errorResponse("SOURCE_NOT_FOUND", "The requested source does not exist.");
  return successResponse(source as Source);
}

export async function getSourceTranscript(sourceId: string) {
  await latency();
  const transcript: Transcript = {
    id: `tr-${sourceId.slice(0, 8)}`,
    source_id: sourceId,
    engine: "faster-whisper",
    engine_version: "1.0.0",
    language: "en",
    full_text: "This is a sample transcript from the video source. It contains the spoken words with proper timestamps and speaker labels for each segment.",
    confidence: 0.92,
    word_timestamps_available: true,
    created_at: new Date().toISOString(),
  };
  return successResponse(transcript);
}

export async function getTranscriptSegments(transcriptId: string) {
  await latency();
  const segments: TranscriptSegment[] = Array.from({ length: 20 }, (_, i) => ({
    id: `seg-${transcriptId.slice(0, 6)}-${i}`,
    transcript_id: transcriptId,
    start_ms: i * 5000,
    end_ms: i * 5000 + 4500,
    speaker_label: i % 2 === 0 ? "SPEAKER_00" : "SPEAKER_01",
    text: `This is segment number ${i + 1} of the transcript with sample spoken text.`,
    confidence: 0.85 + Math.random() * 0.14,
    is_uncertain: false,
    contains_profanity: false,
    metadata_json: null,
  }));
  return successResponse(segments);
}

export async function getSourceScenes(sourceId: string) {
  await latency();
  const scenes: Scene[] = Array.from({ length: 12 }, (_, i) => ({
    id: `sc-${sourceId.slice(0, 6)}-${i}`,
    source_id: sourceId,
    start_ms: i * 30000,
    end_ms: i * 30000 + 28000,
    scene_type: i % 3 === 0 ? "speech" : i % 3 === 1 ? "b-roll" : "reaction",
    motion_score: 0.3 + Math.random() * 0.6,
    face_count: Math.floor(Math.random() * 3),
    active_speaker: i % 2 === 0 ? "SPEAKER_00" : "SPEAKER_01",
    crop_confidence: 0.6 + Math.random() * 0.35,
    metadata_json: null,
  }));
  return successResponse(scenes);
}

// ============================================================
// CANDIDATES
// ============================================================

export async function listCandidates(params: {
  page?: number;
  page_size?: number;
  approval_status?: string;
  profile_id?: string;
  source_id?: string;
  min_score?: number;
} = {}) {
  await latency();
  let data = [...seed.candidates] as Candidate[];
  if (params.approval_status) data = data.filter((c) => c.approval_status === params.approval_status);
  if (params.profile_id) data = data.filter((c) => c.profile_id === params.profile_id);
  if (params.source_id) data = data.filter((c) => c.source_id === params.source_id);
  if (params.min_score) data = data.filter((c) => c.overall_score >= params.min_score!);
  // sort by score desc
  data.sort((a, b) => b.overall_score - a.overall_score);
  const page = params.page || 1;
  const pageSize = params.page_size || 25;
  return paginatedResponse(data, page, pageSize);
}

export async function getCandidate(id: string) {
  await latency();
  const candidate = seed.candidates.find((c) => c.id === id);
  if (!candidate) throw errorResponse("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.");
  return successResponse(candidate as Candidate);
}

export async function getCandidateScores(candidateId: string) {
  await latency();
  const scores = seed.candidateScores.filter((s) => s.candidate_id === candidateId);
  return successResponse(scores as CandidateScore[]);
}

export async function getCandidateEdits(candidateId: string) {
  await latency();
  const edits: CandidateEdit[] = [
    {
      id: `ed-${candidateId.slice(0, 8)}-v1`,
      candidate_id: candidateId,
      version_number: 1,
      start_ms: 30000,
      end_ms: 55000,
      title: "Initial edit",
      caption_text: "You won't believe what happened next! 👀 #fyp #viral",
      crop_configuration_json: { mode: "auto", safe_area: 0.8 },
      branding_preset_id: seed.brandingPresets[0]?.id || null,
      caption_preset_id: seed.captionPresets[0]?.id || null,
      render_preset_id: seed.renderPresets[0]?.id || null,
      edited_by: null,
      created_at: new Date().toISOString(),
    },
  ];
  return successResponse(edits);
}

// ============================================================
// JOBS
// ============================================================

export async function listJobs(params: {
  page?: number;
  page_size?: number;
  status?: string;
  job_type?: string;
  profile_id?: string;
} = {}) {
  await latency();
  let data = [...seed.jobs];
  if (params.status) data = data.filter((j) => j.status === params.status);
  if (params.job_type) data = data.filter((j) => j.job_type === params.job_type);
  if (params.profile_id) data = data.filter((j) => j.profile_id === params.profile_id);
  const page = params.page || 1;
  const pageSize = params.page_size || 25;
  return paginatedResponse(data as Job[], page, pageSize);
}

export async function getJob(id: string) {
  await latency();
  const job = seed.jobs.find((j) => j.id === id);
  if (!job) throw errorResponse("JOB_NOT_FOUND", "The requested job does not exist.");
  return successResponse(job as Job);
}

// ============================================================
// RENDERS
// ============================================================

export async function listRenders(params: { page?: number; page_size?: number; status?: string } = {}) {
  await latency();
  const renders: RenderOutput[] = seed.jobs
    .filter((j) => j.job_type === "render_clip")
    .map((j, i) => ({
      id: `ro-${j.id}`,
      candidate_id: j.entity_id,
      candidate_edit_id: null,
      job_id: j.id,
      render_preset_id: null,
      output_path: `renders/${j.id}/final.mp4`,
      thumbnail_path: `https://picsum.photos/seed/render${i}/320/180`,
      duration_ms: 30000,
      width: 1080,
      height: 1920,
      codec: "h264",
      file_size_bytes: j.output_size || 25_000_000,
      checksum: null,
      status: (j.status === "completed" ? "completed" : j.status === "running" ? "rendering" : j.status === "failed" ? "failed" : "pending") as any,
      created_at: j.created_at,
    }));
  const page = params.page || 1;
  const pageSize = params.page_size || 25;
  return paginatedResponse(renders, page, pageSize);
}

// ============================================================
// SCHEDULES
// ============================================================

export async function listSchedules(params: {
  page?: number;
  page_size?: number;
  status?: string;
  platform?: string;
  profile_id?: string;
  date_from?: string;
  date_to?: string;
} = {}) {
  await latency();
  let data = [...seed.schedules] as Schedule[];
  if (params.status) data = data.filter((s) => s.status === params.status);
  if (params.platform) data = data.filter((s) => s.platform === params.platform);
  if (params.profile_id) data = data.filter((s) => s.profile_id === params.profile_id);
  const page = params.page || 1;
  const pageSize = params.page_size || 100;
  return paginatedResponse(data, page, pageSize);
}

export async function getSchedule(id: string) {
  await latency();
  const schedule = seed.schedules.find((s) => s.id === id);
  if (!schedule) throw errorResponse("SCHEDULE_NOT_FOUND", "The requested schedule does not exist.");
  return successResponse(schedule as Schedule);
}

// ============================================================
// ANALYTICS
// ============================================================

export async function getAnalyticsOverview(params: { range?: string; profile_id?: string } = {}) {
  await latency();
  return successResponse({
    total_views: seed.analyticsData.reduce((sum, d) => sum + d.views, 0),
    total_likes: seed.analyticsData.reduce((sum, d) => sum + d.likes, 0),
    total_comments: seed.analyticsData.reduce((sum, d) => sum + d.comments, 0),
    avg_engagement_rate: 0.087,
    avg_completion_rate: 0.61,
    avg_watch_time_ms: 18300,
    views_change_percent: 12.4,
    engagement_change_percent: 2.1,
    completion_change_percent: 2.8,
    range: params.range || "14d",
  });
}

export async function getAnalyticsTimeseries(params: { range?: string; profile_id?: string } = {}) {
  await latency();
  return successResponse(seed.analyticsData as AnalyticsPoint[]);
}

export async function getHookTypeStats() {
  await latency();
  return successResponse(seed.hookTypeStats as HookTypeStat[]);
}

export async function getClipLengthStats() {
  await latency();
  return successResponse(seed.clipLengthStats as ClipLengthStat[]);
}

export async function getProfilePerformance() {
  await latency();
  return successResponse(seed.profilePerformance as ProfilePerformance[]);
}

// ============================================================
// PRESETS
// ============================================================

export async function getBrandingPresets(profileId?: string) {
  await latency();
  let data = seed.brandingPresets;
  if (profileId) data = data.filter((p) => p.profile_id === profileId);
  return successResponse(data as BrandingPreset[]);
}

export async function getCaptionPresets(profileId?: string) {
  await latency();
  let data = seed.captionPresets;
  if (profileId) data = data.filter((p) => p.profile_id === profileId);
  return successResponse(data as CaptionPreset[]);
}

export async function getRenderPresets(profileId?: string) {
  await latency();
  let data = seed.renderPresets;
  if (profileId) data = data.filter((p) => p.profile_id === profileId);
  return successResponse(data as RenderPreset[]);
}

export async function getScoringPresets(profileId?: string) {
  await latency();
  let data = seed.scoringPresets;
  if (profileId) data = data.filter((p) => p.profile_id === profileId);
  return successResponse(data as ScoringPreset[]);
}

// ============================================================
// NOTIFICATIONS
// ============================================================

export async function listNotifications(params: { page?: number; page_size?: number; unread_only?: boolean } = {}) {
  await latency();
  let data = [...seed.notifications] as Notification[];
  if (params.unread_only) data = data.filter((n) => !n.is_read);
  const page = params.page || 1;
  const pageSize = params.page_size || 25;
  return paginatedResponse(data, page, pageSize);
}

// ============================================================
// SETTINGS
// ============================================================

export async function getSystemSettings() {
  await latency();
  return successResponse({
    max_parallel_jobs: 4,
    gpu_enabled: true,
    default_transcription_model: "large-v3",
    storage_path: "~/CLIPZ",
    max_upload_size_mb: 4096,
    auto_cleanup_temp_hours: 24,
    safety_threshold: 0.5,
    duplicate_threshold: 0.7,
  });
}
