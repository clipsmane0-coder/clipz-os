// ============================================================
// CLIPZ — Shared Type Definitions
// Aligned with CLIPZ Technical Specification v1.0
// ============================================================
//
// Database/API types use snake_case (server convention).
// Frontend uses camelCase (TypeScript convention).
// Use the `convert` utilities in `lib/api/mapper.ts` to
// translate between the two at the API boundary.

// ============================================================
// 1. IDENTIFIERS
// ============================================================

export type UUID = string;

// ============================================================
// 2. ENUMERATIONS
// ============================================================

// --- Profiles ---
export type ProfileType = "general" | "creator" | "topic" | "manual";
export type ProfileStatus = "active" | "paused" | "archived";
export type Platform = "tiktok" | "instagram" | "youtube" | "threads" | "other";

// --- Sources ---
export type SourceStatus =
  | "new"
  | "validating"
  | "queued"
  | "transcribing"
  | "analyzing"
  | "candidates_ready"
  | "needs_review"
  | "completed"
  | "failed"
  | "archived";

export type SourceType = "upload" | "url" | "folder" | "channel";

// --- Candidates ---
export type ApprovalStatus = "pending" | "approved" | "rejected" | "needs_changes" | "archived";

export type ScoreSignal =
  | "hook_strength"
  | "context_completeness"
  | "emotional_intensity"
  | "profile_match"
  | "payoff_strength"
  | "visual_activity"
  | "topic_relevance"
  | "length_fit"
  | "novelty"
  | "silence_penalty"
  | "duplicate_penalty"
  | "confusion_penalty"
  | "policy_risk";

export type SafetyStatus = "safe" | "review" | "flagged" | "blocked";
export type RightsStatus = "owned" | "licensed" | "creator_approved" | "transformative_review" | "unknown" | "blocked";

// --- Jobs ---
export type JobType =
  | "validate_source"
  | "generate_proxy"
  | "transcribe"
  | "detect_scenes"
  | "analyze_source"
  | "generate_candidates"
  | "detect_duplicates"
  | "generate_preview"
  | "render_clip"
  | "build_export"
  | "publish_post"
  | "fetch_analytics"
  | "cleanup_storage";

export type JobStatus =
  | "pending"
  | "queued"
  | "running"
  | "paused"
  | "retrying"
  | "completed"
  | "failed"
  | "cancelled";

export type JobPriority = "urgent" | "high" | "normal" | "low";
export type EntityType = "profile" | "source" | "candidate" | "render" | "schedule" | "post";

// --- Renders ---
export type RenderStatus = "pending" | "rendering" | "completed" | "failed" | "cancelled";

// --- Exports ---
export type ExportStatus = "pending" | "building" | "ready" | "failed" | "downloaded";

// --- Schedules ---
export type ScheduleStatus = "draft" | "scheduled" | "ready" | "publishing" | "published" | "failed" | "cancelled";

// --- Platform posts ---
export type PostStatus = "draft" | "publishing" | "published" | "failed" | "deleted";

// --- Duplicates ---
export type SimilarityType = "transcript" | "audio" | "visual" | "combined";
export type DuplicateStatus = "unique" | "near_duplicate" | "exact_duplicate" | "review";

// --- Notifications ---
export type NotificationType = "success" | "warning" | "error" | "action_required" | "informational";

// --- Preset types ---
export type PresetStatus = "draft" | "active" | "deprecated" | "archived";

// ============================================================
// 3. CORE DATABASE ENTITIES (snake_case — API shape)
// ============================================================

export interface User {
  id: UUID;
  email: string;
  display_name: string;
  role: "owner" | "admin" | "editor" | "reviewer" | "viewer";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Profile {
  id: UUID;
  name: string;
  slug: string;
  profile_type: ProfileType;
  description: string;
  avatar_path: string | null;
  language: string;
  status: ProfileStatus;
  auto_approval_enabled: boolean;
  default_processing_mode: "balanced" | "speed" | "quality";
  default_rights_status: RightsStatus;
  created_by: UUID | null;
  created_at: string;
  updated_at: string;
  // Aggregated display fields (from related tables)
  clips_published?: number;
  clips_queued?: number;
}

export interface ProfilePlatform {
  id: UUID;
  profile_id: UUID;
  platform: Platform;
  handle: string;
  account_id: string | null;
  is_connected: boolean;
  posting_enabled: boolean;
  daily_post_limit: number;
  timezone: string;
  credentials_reference: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileSource {
  id: UUID;
  profile_id: UUID;
  source_type: SourceType;
  source_url: string | null;
  source_name: string;
  authorization_status: "unauthorized" | "authorized" | "expired" | "revoked";
  watcher_enabled: boolean;
  last_checked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: UUID;
  profile_id: UUID;
  title: string;
  source_type: SourceType;
  original_filename: string | null;
  source_url: string | null;
  local_path: string | null;
  file_hash: string | null;
  audio_fingerprint: string | null;
  visual_fingerprint: string | null;
  duration_ms: number;
  width: number;
  height: number;
  frame_rate: number;
  codec: string | null;
  file_size_bytes: number;
  language: string;
  rights_status: RightsStatus;
  status: SourceStatus;
  error_code: string | null;
  error_message: string | null;
  imported_at: string;
  created_at: string;
  updated_at: string;
  // Computed display fields
  thumbnail_path?: string;
  candidates_count?: number;
}

export interface SourceFile {
  id: UUID;
  source_id: UUID;
  file_type: "original" | "proxy" | "audio" | "thumbnail";
  path: string;
  file_size_bytes: number;
  checksum: string | null;
  created_at: string;
}

export interface Transcript {
  id: UUID;
  source_id: UUID;
  engine: string;
  engine_version: string;
  language: string;
  full_text: string;
  confidence: number;
  word_timestamps_available: boolean;
  created_at: string;
}

export interface TranscriptSegment {
  id: UUID;
  transcript_id: UUID;
  start_ms: number;
  end_ms: number;
  speaker_label: string | null;
  text: string;
  confidence: number;
  is_uncertain: boolean;
  contains_profanity: boolean;
  metadata_json: Record<string, unknown> | null;
}

export interface Scene {
  id: UUID;
  source_id: UUID;
  start_ms: number;
  end_ms: number;
  scene_type: string | null;
  motion_score: number;
  face_count: number;
  active_speaker: string | null;
  crop_confidence: number;
  metadata_json: Record<string, unknown> | null;
}

export interface AnalysisRun {
  id: UUID;
  source_id: UUID;
  scoring_preset_id: UUID | null;
  model_name: string;
  model_version: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string | null;
  completed_at: string | null;
  configuration_json: Record<string, unknown> | null;
  error_code: string | null;
  error_message: string | null;
}

export interface Candidate {
  id: UUID;
  source_id: UUID;
  analysis_run_id: UUID | null;
  profile_id: UUID;
  start_ms: number;
  end_ms: number;
  duration_ms: number;
  title: string;
  transcript_excerpt: string;
  hook_text: string;
  selection_reason: string;
  overall_score: number;
  crop_confidence: number;
  audio_quality_score: number;
  visual_quality_score: number;
  duplicate_risk: number;
  safety_status: SafetyStatus;
  rights_status: RightsStatus;
  approval_status: ApprovalStatus;
  recommended_platform: Platform;
  created_at: string;
  updated_at: string;
  // Computed / related display fields
  thumbnail_path?: string;
  source_title?: string;
  profile_name?: string;
  score_breakdown?: CandidateScore[];
  views?: number;
  likes?: number;
  comments?: number;
  platform?: Platform;
  published_at?: string;
}

export interface CandidateScore {
  id: UUID;
  candidate_id: UUID;
  signal_name: ScoreSignal;
  raw_value: number;
  normalized_value: number;
  weight: number;
  weighted_score: number;
  explanation: string;
  created_at: string;
}

export interface CandidateEdit {
  id: UUID;
  candidate_id: UUID;
  version_number: number;
  start_ms: number;
  end_ms: number;
  title: string;
  caption_text: string;
  crop_configuration_json: Record<string, unknown> | null;
  branding_preset_id: UUID | null;
  caption_preset_id: UUID | null;
  render_preset_id: UUID | null;
  edited_by: UUID | null;
  created_at: string;
}

export interface DuplicateMatch {
  id: UUID;
  candidate_id: UUID;
  matched_candidate_id: UUID | null;
  matched_post_id: UUID | null;
  similarity_type: SimilarityType;
  transcript_similarity: number;
  audio_similarity: number;
  visual_similarity: number;
  overall_similarity: number;
  status: DuplicateStatus;
  created_at: string;
}

export interface Job {
  id: UUID;
  job_type: JobType;
  entity_type: EntityType;
  entity_id: UUID;
  profile_id: UUID | null;
  priority: JobPriority;
  status: JobStatus;
  progress_percent: number;
  attempts: number;
  max_attempts: number;
  retryable: boolean;
  locked_by: string | null;
  locked_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_code: string | null;
  error_message: string | null;
  payload_json: Record<string, unknown> | null;
  result_json: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  // Display fields
  entity_title?: string;
  profile_name?: string;
  render_device?: string;
  render_preset?: string;
  estimated_time?: string;
  output_size?: number;
}

export interface RenderOutput {
  id: UUID;
  candidate_id: UUID;
  candidate_edit_id: UUID | null;
  job_id: UUID | null;
  render_preset_id: UUID | null;
  output_path: string;
  thumbnail_path: string;
  duration_ms: number;
  width: number;
  height: number;
  codec: string;
  file_size_bytes: number;
  checksum: string | null;
  status: RenderStatus;
  created_at: string;
}

export interface ExportPackage {
  id: UUID;
  render_output_id: UUID;
  profile_id: UUID;
  package_path: string;
  manifest_path: string;
  status: ExportStatus;
  created_at: string;
}

export interface Schedule {
  id: UUID;
  profile_id: UUID;
  render_output_id: UUID | null;
  candidate_id: UUID | null;
  platform: Platform;
  scheduled_for: string;
  timezone: string;
  status: ScheduleStatus;
  priority: "normal" | "high" | "low";
  notes: string | null;
  created_at: string;
  updated_at: string;
  // Display fields
  clip_title?: string;
  thumbnail_path?: string;
  profile_name?: string;
}

export interface PlatformPost {
  id: UUID;
  schedule_id: UUID;
  platform: Platform;
  external_post_id: string | null;
  external_url: string | null;
  title: string;
  caption: string;
  hashtags_json: string[] | null;
  published_at: string | null;
  status: PostStatus;
  error_code: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsSnapshot {
  id: UUID;
  platform_post_id: UUID;
  captured_at: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  average_watch_time_ms: number;
  completion_rate: number;
  rewatches: number;
  followers_gained: number;
  raw_payload_json: Record<string, unknown> | null;
}

export interface RightsReview {
  id: UUID;
  source_id: UUID | null;
  candidate_id: UUID | null;
  rights_status: RightsStatus;
  reviewer_id: UUID | null;
  notes: string | null;
  reviewed_at: string;
}

export interface SafetyReview {
  id: UUID;
  source_id: UUID | null;
  candidate_id: UUID | null;
  status: SafetyStatus;
  flags_json: string[] | null;
  reviewer_id: UUID | null;
  notes: string | null;
  reviewed_at: string;
}

export interface Notification {
  id: UUID;
  user_id: UUID | null;
  type: NotificationType;
  title: string;
  message: string;
  entity_type: EntityType | null;
  entity_id: UUID | null;
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: UUID;
  user_id: UUID | null;
  action: string;
  entity_type: EntityType;
  entity_id: UUID;
  old_values_json: Record<string, unknown> | null;
  new_values_json: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface SystemSetting {
  id: UUID;
  key: string;
  value: string;
  value_type: "string" | "number" | "boolean" | "json";
  description: string | null;
  updated_at: string;
}

export interface ProfileSetting {
  id: UUID;
  profile_id: UUID;
  key: string;
  value: string;
  value_type: "string" | "number" | "boolean" | "json";
  updated_at: string;
}

// ============================================================
// 4. PRESETS
// ============================================================

export interface BrandingPreset {
  id: UUID;
  profile_id: UUID;
  name: string;
  version: number;
  is_active: boolean;
  logo_path: string | null;
  watermark: boolean;
  watermark_position: string;
  outro_duration_ms: number;
  color_primary: string | null;
  color_secondary: string | null;
  created_at: string;
}

export interface CaptionPreset {
  id: UUID;
  profile_id: UUID;
  name: string;
  version: number;
  is_active: boolean;
  font_family: string;
  font_size: number;
  font_color: string;
  stroke_color: string;
  stroke_width: number;
  background_enabled: boolean;
  background_color: string;
  background_opacity: number;
  position: "bottom" | "top" | "middle";
  max_lines: number;
  highlight_enabled: boolean;
  highlight_color: string;
  created_at: string;
}

export interface RenderPreset {
  id: UUID;
  profile_id: UUID;
  name: string;
  version: number;
  is_active: boolean;
  resolution: string;
  aspect_ratio: string;
  frame_rate: number;
  codec: string;
  bitrate_kbps: number;
  audio_codec: string;
  audio_bitrate_kbps: number;
  crop_strategy: "auto" | "center" | "top" | "manual";
  enhancement_mode: "off" | "light" | "standard" | "high";
  platform_target: Platform | null;
  created_at: string;
}

export interface ScoringPreset {
  id: UUID;
  profile_id: UUID;
  name: string;
  version: number;
  is_active: boolean;
  weights_json: Record<string, number>;
  thresholds_json: Record<string, number>;
  created_at: string;
}

// ============================================================
// 5. API RESPONSE WRAPPERS
// ============================================================

export interface ApiResponse<T> {
  success: true;
  data: T;
  meta: {
    request_id: string;
  };
}

export interface PaginatedResponse<T> {
  success: true;
  data: T[];
  meta: {
    page: number;
    page_size: number;
    total: number;
    request_id: string;
  };
}

export interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
    retryable: boolean;
  };
  meta: {
    request_id: string;
  };
}

// ============================================================
// 6. DASHBOARD / SPECIALIZED COMPOSITES
// ============================================================

export interface DashboardOverview {
  active_profile_count: number;
  sources_processing: number;
  candidates_awaiting_review: number;
  active_render_jobs: number;
  scheduled_posts: number;
  failed_jobs: number;
  storage_utilization_bytes: number;
  storage_total_bytes: number;
  worker_health: {
    api: boolean;
    database: boolean;
    worker: boolean;
    ffmpeg: boolean;
    transcription: boolean;
    storage: boolean;
  };
  recent_activity: ActivityItem[];
  recent_analytics: {
    total_views_7d: number;
    total_engagement_7d: number;
    completion_rate_avg: number;
    views_change_percent: number;
  };
  top_hook_types: HookTypeStat[];
  chart_data: AnalyticsPoint[];
  upcoming_schedules: Schedule[];
}

export interface ActivityItem {
  id: string;
  type: string;
  message: string;
  entity_type: EntityType;
  entity_id: string;
  timestamp: string;
}

export interface HookTypeStat {
  type: string;
  count: number;
  avg_views: number;
  avg_completion: number;
}

export interface ClipLengthStat {
  length: string;
  count: number;
  avg_views: number;
  avg_completion: number;
}

export interface AnalyticsPoint {
  date: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  clips_posted: number;
}

export interface ProfilePerformance {
  profile_id: UUID;
  profile_name: string;
  clips_count: number;
  total_views: number;
  engagement_rate: number;
  completion_rate: number;
  avg_score: number;
}
