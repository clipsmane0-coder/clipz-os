// ============================================================
// CLIPZ — API Data Mapper
// ============================================================
// Translates between snake_case (API / database) and
// camelCase (frontend) at the API boundary.
//
// Frontend code uses camelCase exclusively.
// API wire format is snake_case per the technical spec.
// ============================================================

import type {
  Profile,
  Source,
  Candidate,
  CandidateScore,
  Job,
  Schedule,
  RenderOutput,
  Transcript,
  TranscriptSegment,
  Scene,
  AnalysisRun,
  DuplicateMatch,
  Notification,
  BrandingPreset,
  CaptionPreset,
  RenderPreset,
  ScoringPreset,
  ProfilePlatform,
  ProfileSource,
  PlatformPost,
  AnalyticsSnapshot,
  DashboardOverview,
  ProfilePerformance,
} from "../types/clipz";

// --- Frontend (camelCase) type definitions ---

export type FProfile = CamelCased<Profile>;
export type FProfilePlatform = CamelCased<ProfilePlatform>;
export type FProfileSource = CamelCased<ProfileSource>;
export type FSource = CamelCased<Source>;
export type FCandidate = CamelCased<Candidate>;
export type FCandidateScore = CamelCased<CandidateScore>;
export type FJob = CamelCased<Job>;
export type FSchedule = CamelCased<Schedule>;
export type FRenderOutput = CamelCased<RenderOutput>;
export type FTranscript = CamelCased<Transcript>;
export type FTranscriptSegment = CamelCased<TranscriptSegment>;
export type FScene = CamelCased<Scene>;
export type FAnalysisRun = CamelCased<AnalysisRun>;
export type FDuplicateMatch = CamelCased<DuplicateMatch>;
export type FNotification = CamelCased<Notification>;
export type FBrandingPreset = CamelCased<BrandingPreset>;
export type FCaptionPreset = CamelCased<CaptionPreset>;
export type FRenderPreset = CamelCased<RenderPreset>;
export type FScoringPreset = CamelCased<ScoringPreset>;
export type FPlatformPost = CamelCased<PlatformPost>;
export type FAnalyticsSnapshot = CamelCased<AnalyticsSnapshot>;
export type FDashboardOverview = CamelCased<DashboardOverview>;
export type FProfilePerformance = CamelCased<ProfilePerformance>;

// ---- Utility types ----

type CamelCased<T> = T extends (infer U)[]
  ? CamelCased<U>[]
  : T extends object
  ? { [K in keyof T as K extends string ? CamelCase<K> : K]: CamelCased<T[K]> }
  : T;

type CamelCase<S extends string> = S extends `${infer First}_${infer Rest}`
  ? `${First}${Capitalize<CamelCase<Rest>>}`
  : S;

// ---- View model types (composed for UI display) ----

export type FProfileView = FProfile & {
  platforms: FProfilePlatform[];
  profileSources: FProfileSource[];
  clipsPublished: number;
  clipsQueued: number;
  targetPlatforms: string[];
  sourceChannels: string[];
  postingSchedule: Record<string, number>;
  clipLengths: { min: number; max: number };
  contentThemes: string[];
  safetyLevel: string;
  image: string;
  type: FProfile["profileType"];
  rightsStatus: FProfile["defaultRightsStatus"];
  autoApproval: FProfile["autoApprovalEnabled"];
};

export type FSourceView = FSource & {
  profileName: string;
  thumbnail: string;
  filename: string;
  sourceUrl: string;
  duration: number;
  resolution: string;
  fps: number;
  fileSize: string;
  dateAdded: string;
  duplicateStatus: string;
  candidatesFound: number;
  progress: number;
  rightsStatus: FSource["rightsStatus"];
};

export type FCandidateView = Omit<FCandidate, "scoreBreakdown" | "recommendedPlatform" | "hookText" | "transcriptExcerpt" | "thumbnailPath" | "startMs" | "endMs" | "durationMs" | "audioQualityScore" | "visualQualityScore" | "duplicateRisk" | "approvalStatus" | "selectionReason" | "sourceTitle" | "profileName"> & {
  sourceTitle: string;
  profileName: string;
  thumbnail: string;
  startTime: number;
  endTime: number;
  duration: number;
  hook: string;
  transcript: string;
  whySelected: string[];
  riskFlags: string[];
  similarity: number;
  audioQuality: number;
  visualQuality: number;
  recommendedPlatform: string;
  suggestedCaption: string;
  suggestedHashtags: string[];
  scoreBreakdown: Record<string, number>;
  status: string;
};

export type FJobView = Omit<FJob, "status"> & {
  clipTitle: string;
  clipId: string;
  device: string;
  progress: number;
  errorMessage: string | null;
  retryCount: number;
  outputSize: string | null;
  status: string;
};

export type FScheduleView = FSchedule & {
  clipId: string | null;
  clipTitle: string;
  thumbnail: string;
  scheduledDate: string;
  scheduledTime: string;
};

export type FLibraryItem = Omit<FCandidateView, "recommendedPlatform"> & {
  views: number;
  likes: number;
  comments: number;
  platform: string;
  publishedAt: string | null;
};

// ============================================================
// Generic conversion
// ============================================================

function toCamel(s: string): string {
  return s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function toSnake(s: string): string {
  return s.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
}

/** Deep-convert an object (or array) from snake_case to camelCase. */
export function snakeToCamel<T = any>(obj: any): CamelCased<T> {
  if (obj === null || obj === undefined) return obj as CamelCased<T>;
  if (Array.isArray(obj)) return obj.map((v) => snakeToCamel(v)) as CamelCased<T>;
  if (typeof obj !== "object") return obj as CamelCased<T>;

  const result: Record<string, any> = {};
  for (const key of Object.keys(obj)) {
    result[toCamel(key)] = snakeToCamel(obj[key]);
  }
  return result as CamelCased<T>;
}

/** Deep-convert an object (or array) from camelCase to snake_case. */
export function camelToSnake<T = any>(obj: any): T {
  if (obj === null || obj === undefined) return obj as T;
  if (Array.isArray(obj)) return obj.map((v) => camelToSnake(v)) as T;
  if (typeof obj !== "object") return obj as T;

  const result: Record<string, any> = {};
  for (const key of Object.keys(obj)) {
    result[toSnake(key)] = camelToSnake(obj[key]);
  }
  return result as T;
}

// ============================================================
// Response envelope helpers
// ============================================================

/** Unwrap a paginated API response, converting data to camelCase. */
export function unwrapList<T>(response: any): { data: CamelCased<T>[]; total: number; page: number; pageSize: number } {
  return {
    data: snakeToCamel<T[]>(response.data),
    total: response.meta.total,
    page: response.meta.page,
    pageSize: response.meta.page_size,
  };
}

/** Unwrap a single-item API response, converting data to camelCase. */
export function unwrap<T>(response: any): CamelCased<T> {
  return snakeToCamel<T>(response.data);
}
