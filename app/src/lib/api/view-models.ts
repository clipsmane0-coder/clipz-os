// ============================================================
// CLIPZ — View Model Composers
// ============================================================
// Compose core database entities into UI-ready view models.
// These functions add display-oriented fields (formatting,
// composed references, display names) without modifying
// the underlying entity types.
// ============================================================

import type {
  FProfile,
  FProfilePlatform,
  FProfileSource,
  FSource,
  FCandidate,
  FCandidateScore,
  FJob,
  FSchedule,
  FProfileView,
  FSourceView,
  FCandidateView,
  FJobView,
  FScheduleView,
  FLibraryItem,
} from "./mapper";

const PLATFORM_LABELS: Record<string, string> = {
  tiktok: "TikTok",
  instagram: "Instagram",
  youtube: "YouTube Shorts",
  threads: "Threads",
  other: "Other",
};

export function composeProfileView(
  profile: FProfile,
  platforms: FProfilePlatform[] = [],
  sources: FProfileSource[] = []
): FProfileView {
  const targetPlatforms = platforms
    .filter((p) => p.isConnected)
    .map((p) => PLATFORM_LABELS[p.platform] || p.platform);

  const sourceChannels = sources.map((s) => s.sourceName);

  const postingSchedule: Record<string, number> = {};
  platforms.forEach((p) => {
    if (p.postingEnabled) {
      postingSchedule[PLATFORM_LABELS[p.platform] || p.platform] = p.dailyPostLimit;
    }
  });

  return {
    ...profile,
    platforms,
    profileSources: sources,
    clipsPublished: profile.clipsPublished || 0,
    clipsQueued: profile.clipsQueued || 0,
    targetPlatforms: targetPlatforms.length ? targetPlatforms : ["TikTok", "Instagram", "YouTube Shorts"],
    sourceChannels: sourceChannels.length ? sourceChannels : ["YouTube", "Twitch"],
    postingSchedule: Object.keys(postingSchedule).length
      ? postingSchedule
      : { TikTok: 3, Instagram: 2, "YouTube Shorts": 2 },
    clipLengths: { min: 15, max: 60 },
    contentThemes: ["General"],
    safetyLevel: "moderate",
    image: profile.avatarPath || "",
    type: profile.profileType,
    rightsStatus: profile.defaultRightsStatus,
    autoApproval: profile.autoApprovalEnabled,
  };
}

export function composeSourceView(source: FSource, profileName = ""): FSourceView {
  const durationSec = Math.round(source.durationMs / 1000);
  const fileSizeGB = source.fileSizeBytes / (1024 * 1024 * 1024);

  let progress = 0;
  switch (source.status) {
    case "new":
      progress = 5;
      break;
    case "validating":
      progress = 15;
      break;
    case "queued":
      progress = 20;
      break;
    case "transcribing":
      progress = 45;
      break;
    case "analyzing":
      progress = 70;
      break;
    case "candidates_ready":
    case "completed":
      progress = 100;
      break;
    case "needs_review":
      progress = 95;
      break;
    case "failed":
      progress = 0;
      break;
    default:
      progress = 10;
  }

  return {
    ...source,
    profileName,
    thumbnail: source.thumbnailPath || "",
    filename: source.originalFilename || "untitled.mp4",
    sourceUrl: source.sourceUrl || "",
    duration: durationSec,
    resolution: `${source.width}x${source.height}`,
    fps: source.frameRate,
    fileSize: fileSizeGB >= 1 ? `${fileSizeGB.toFixed(1)} GB` : `${(fileSizeGB * 1024).toFixed(0)} MB`,
    dateAdded: source.importedAt,
    duplicateStatus: "unique",
    candidatesFound: source.candidatesCount || 0,
    progress,
    rightsStatus: source.rightsStatus,
  } as FSourceView;
}

export function composeCandidateView(
  candidate: FCandidate,
  scores: FCandidateScore[] = [],
  sourceTitle = "",
  profileName = ""
): FCandidateView {
  const scoreBreakdown: Record<string, number> = {};
  scores.forEach((s) => {
    scoreBreakdown[s.signalName] = s.weightedScore;
  });

  return {
    ...candidate,
    sourceTitle: sourceTitle || candidate.sourceTitle || "",
    profileName: profileName || candidate.profileName || "",
    thumbnail: candidate.thumbnailPath || "",
    startTime: Math.round(candidate.startMs / 1000),
    endTime: Math.round(candidate.endMs / 1000),
    duration: Math.round(candidate.durationMs / 1000),
    hook: candidate.hookText,
    transcript: candidate.transcriptExcerpt,
    whySelected: [candidate.selectionReason, "Strong hook", "Clear narrative"],
    riskFlags: [],
    similarity: candidate.duplicateRisk,
    audioQuality: candidate.audioQualityScore,
    visualQuality: candidate.visualQualityScore,
    recommendedPlatform: PLATFORM_LABELS[candidate.recommendedPlatform] || candidate.recommendedPlatform,
    suggestedCaption: `${candidate.hookText} 👀 #fyp #viral`,
    suggestedHashtags: ["fyp", "viral", "trending", "foryou"],
    scoreBreakdown,
    status: candidate.approvalStatus === "pending" ? "new" : candidate.approvalStatus,
  } as FCandidateView;
}

export function composeJobView(job: FJob): FJobView {
  const outputSizeBytes = job.outputSize || 0;
  // Map spec status to UI display status for backwards compatibility
  const displayStatus: Record<string, string> = {
    pending: "queued",
    queued: "queued",
    running: "rendering",
    paused: "paused",
    retrying: "rendering",
    completed: "completed",
    failed: "failed",
    cancelled: "cancelled",
  };
  return {
    ...job,
    clipTitle: job.entityTitle || "Untitled clip",
    clipId: job.entityId,
    device: job.renderDevice || "GPU",
    progress: job.progressPercent,
    errorMessage: job.errorMessage,
    retryCount: job.attempts,
    outputSize: outputSizeBytes
      ? `${(outputSizeBytes / (1024 * 1024)).toFixed(0)} MB`
      : null,
    // Override status for UI display compatibility
    status: displayStatus[job.status] || job.status,
  } as FJobView;
}

export function composeScheduleView(schedule: FSchedule): FScheduleView {
  const dt = new Date(schedule.scheduledFor);
  return {
    ...schedule,
    clipId: schedule.candidateId,
    clipTitle: schedule.clipTitle || "Untitled",
    thumbnail: schedule.thumbnailPath || "",
    scheduledDate: dt.toISOString().split("T")[0],
    scheduledTime: dt.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }),
  };
}

export function composeLibraryItem(
  candidate: FCandidate,
  scores: FCandidateScore[] = [],
  extra: { views?: number; likes?: number; comments?: number; platform?: string; publishedAt?: string } = {}
): FLibraryItem {
  const base = composeCandidateView(candidate, scores);
  return {
    ...base,
    views: extra.views || 0,
    likes: extra.likes || 0,
    comments: extra.comments || 0,
    platform: extra.platform || "tiktok",
    publishedAt: extra.publishedAt || null,
  } as FLibraryItem;
}
