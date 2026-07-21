// ============================================================
// CLIPZ — Mock Data (Compatibility Layer)
// ============================================================
// DEPRECATED: Use lib/api/hooks instead.
//
// This file re-exports data from the spec-aligned mock API layer
// in a backwards-compatible shape so existing components keep working.
// New code should use the TanStack Query hooks in lib/api/hooks.ts.
// ============================================================

import * as seed from "./api/mock-seed";
import { snakeToCamel } from "./api/mapper";

// --- Re-export spec types for backwards compat ---
export type {
  ProfileType,
  ProfileStatus,
  Platform,
  SourceStatus,
  SourceType,
  ApprovalStatus,
  ScoreSignal,
  SafetyStatus,
  RightsStatus,
  JobType,
  JobStatus,
  JobPriority,
  EntityType,
  RenderStatus,
  ScheduleStatus,
  PostStatus,
  DuplicateStatus,
  NotificationType,
} from "./types/clipz";

// --- Convert seed data to camelCase for frontend ---
const profilesRaw = snakeToCamel<any[]>(seed.profiles);
const sourcesRaw = snakeToCamel<any[]>(seed.sources);
const candidatesRaw = snakeToCamel<any[]>(seed.candidates);
const jobsRaw = snakeToCamel<any[]>(seed.jobs);
const schedulesRaw = snakeToCamel<any[]>(seed.schedules);

// --- Backwards-compatible profile shape ---
export interface Profile {
  id: string;
  name: string;
  type: ProfileType;
  description: string;
  image: string;
  sourceChannels: string[];
  targetPlatforms: string[];
  clipLengths: { min: number; max: number };
  contentThemes: string[];
  clipsPublished: number;
  clipsQueued: number;
  status: ProfileStatus | "draft";
  rightsStatus: string;
  autoApproval: boolean;
  safetyLevel: string;
  postingSchedule: Record<string, number>;
}

export const profiles: Profile[] = profilesRaw.map((p: any) => ({
  id: p.id,
  name: p.name,
  type: p.profileType,
  description: p.description,
  image: p.avatarPath,
  sourceChannels: ["YouTube", "Twitch"],
  targetPlatforms: ["TikTok", "Instagram", "YouTube Shorts", "Threads"],
  clipLengths: { min: 15, max: 60 },
  contentThemes: ["General"],
  clipsPublished: p.clipsPublished || 0,
  clipsQueued: p.clipsQueued || 0,
  status: p.status,
  rightsStatus: p.defaultRightsStatus,
  autoApproval: p.autoApprovalEnabled,
  safetyLevel: "moderate",
  postingSchedule: { TikTok: 3, Instagram: 2, "YouTube Shorts": 2 },
}));

// --- Backwards-compatible source shape ---
export interface SourceVideo {
  id: string;
  profileId: string;
  title: string;
  sourceUrl: string;
  sourceType: SourceType;
  filename: string;
  duration: number;
  resolution: string;
  fps: number;
  fileSize: string;
  dateAdded: string;
  status: SourceStatus;
  progress: number;
  rightsStatus: string;
  duplicateStatus: "unique" | "near_duplicate" | "exact_duplicate";
  candidatesFound: number;
  thumbnail: string;
}

export const sourceVideos: SourceVideo[] = sourcesRaw.map((s: any) => ({
  id: s.id,
  profileId: s.profileId,
  title: s.title,
  sourceUrl: s.sourceUrl || "",
  sourceType: s.sourceType,
  filename: s.originalFilename || "upload.mp4",
  duration: Math.round(s.durationMs / 1000),
  resolution: `${s.width}x${s.height}`,
  fps: s.frameRate,
  fileSize: `${(s.fileSizeBytes / (1024 * 1024 * 1024)).toFixed(1)} GB`,
  dateAdded: s.importedAt,
  status: s.status,
  progress: s.status === "transcribing" ? 78 : s.status === "analyzing" ? 45 : s.status === "candidates_ready" ? 100 : s.status === "completed" ? 100 : 15,
  rightsStatus: s.rightsStatus,
  duplicateStatus: "unique",
  candidatesFound: s.candidatesCount || 0,
  thumbnail: s.thumbnailPath,
}));

// --- Backwards-compatible candidate shape ---
export interface CandidateClip {
  id: string;
  sourceId: string;
  profileId: string;
  score: number;
  scoreBreakdown: Record<string, number>;
  startTime: number;
  endTime: number;
  duration: number;
  hook: string;
  title: string;
  transcript: string;
  whySelected: string[];
  riskFlags: string[];
  similarity: number;
  cropConfidence: number;
  audioQuality: number;
  visualQuality: number;
  recommendedPlatform: string;
  suggestedCaption: string;
  suggestedHashtags: string[];
  status: "new" | "reviewing" | "approved" | "rejected" | "rendering" | "rendered" | "scheduled" | "published" | "archived";
  thumbnail: string;
}

export const candidateClips: CandidateClip[] = candidatesRaw.map((c: any) => ({
  id: c.id,
  sourceId: c.sourceId,
  profileId: c.profileId,
  score: c.overallScore,
  scoreBreakdown: c.scoreBreakdown
    ? Object.fromEntries(c.scoreBreakdown.map((s: any) => [s.signalName, s.weightedScore]))
    : {},
  startTime: Math.round(c.startMs / 1000),
  endTime: Math.round(c.endMs / 1000),
  duration: Math.round(c.durationMs / 1000),
  hook: c.hookText,
  title: c.title,
  transcript: c.transcriptExcerpt,
  whySelected: [c.selectionReason, "High hook strength", "Good narrative flow"],
  riskFlags: [],
  similarity: c.duplicateRisk,
  cropConfidence: c.cropConfidence,
  audioQuality: c.audioQualityScore,
  visualQuality: c.visualQualityScore,
  recommendedPlatform: c.recommendedPlatform,
  suggestedCaption: "You won't believe what happened next! 👀 #fyp #viral",
  suggestedHashtags: ["fyp", "viral", "trending", "foryou"],
  status: (c.approvalStatus === "pending" ? "new" : c.approvalStatus) as any,
  thumbnail: c.thumbnailPath,
}));

// --- Backwards-compatible render job shape ---
export interface RenderJob {
  id: string;
  clipId: string;
  profileId: string;
  clipTitle: string;
  priority: "urgent" | "high" | "normal" | "low";
  status: "queued" | "rendering" | "completed" | "failed";
  progress: number;
  renderPreset: string;
  estimatedTime: string;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
  retryCount: number;
  outputSize?: string;
  device: string;
}

export const renderJobs: RenderJob[] = jobsRaw
  .filter((j: any) => j.jobType === "render_clip")
  .map((j: any) => ({
    id: j.id,
    clipId: j.entityId,
    profileId: j.profileId,
    clipTitle: j.entityTitle || "Untitled clip",
    priority: j.priority,
    status: (j.status === "running" ? "rendering" : j.status === "completed" ? "completed" : j.status === "failed" ? "failed" : "queued") as any,
    progress: j.progressPercent,
    renderPreset: j.renderPreset || "Default",
    estimatedTime: j.estimatedTime || "5m 00s",
    startedAt: j.startedAt,
    completedAt: j.completedAt,
    errorMessage: j.errorMessage,
    retryCount: j.attempts,
    outputSize: j.outputSize ? `${(j.outputSize / (1024 * 1024)).toFixed(0)} MB` : undefined,
    device: j.renderDevice || "GPU",
  }));

// --- Backwards-compatible scheduled post shape ---
export interface ScheduledPost {
  id: string;
  clipId: string;
  clipTitle: string;
  profileId: string;
  platform: string;
  scheduledDate: string;
  scheduledTime: string;
  status: "scheduled" | "published" | "failed";
  thumbnail: string;
}

export const scheduledPosts: ScheduledPost[] = schedulesRaw.map((s: any) => {
  const dt = new Date(s.scheduledFor);
  return {
    id: s.id,
    clipId: s.candidateId || "",
    clipTitle: s.clipTitle || "Untitled",
    profileId: s.profileId,
    platform: s.platform,
    scheduledDate: dt.toISOString().split("T")[0],
    scheduledTime: dt.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }),
    status: s.status === "published" ? "published" : s.status === "failed" ? "failed" : "scheduled",
    thumbnail: s.thumbnailPath,
  };
});

// --- Analytics data (keep original shape) ---
export interface AnalyticsPoint {
  date: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  clipsPosted: number;
}

export const analyticsData: AnalyticsPoint[] = seed.analyticsData.map((d) => ({
  date: d.date,
  views: d.views,
  likes: d.likes,
  comments: d.comments,
  shares: d.shares,
  clipsPosted: d.clips_posted,
}));

export interface HookTypeStat {
  type: string;
  count: number;
  avgViews: number;
  avgCompletion: number;
}

export const hookTypeStats: HookTypeStat[] = seed.hookTypeStats.map((h) => ({
  type: h.type,
  count: h.count,
  avgViews: h.avg_views,
  avgCompletion: h.avg_completion,
}));

export interface ClipLengthStat {
  length: string;
  count: number;
  avgViews: number;
  avgCompletion: number;
}

export const clipLengthStats: ClipLengthStat[] = seed.clipLengthStats.map((c) => ({
  length: c.length,
  count: c.count,
  avgViews: c.avg_views,
  avgCompletion: c.avg_completion,
}));

// --- Totals (computed from seed) ---
export const totals = {
  totalViews: "847,230",
  clipsPublished: "2,456",
  clipsThisWeek: 28,
  avgCompletionRate: "61%",
  candidatesReady: candidatesRaw.filter((c: any) => c.approvalStatus === "pending").length,
  sourcesProcessing: sourcesRaw.filter((s: any) => s.status === "transcribing" || s.status === "analyzing").length,
  storageUsed: "342 GB / 1TB",
  avgWatchTime: "18.3s",
  engagementRate: "8.7%",
};
