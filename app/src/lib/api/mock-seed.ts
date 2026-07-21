// ============================================================
// CLIPZ — Mock Seed Data
// ============================================================
// Data is stored in snake_case to match future API responses.
// The mock API service converts to camelCase at the boundary
// using the mapper utility.
// ============================================================

import type {
  Profile,
  ProfilePlatform,
  ProfileSource,
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
  Notification,
  BrandingPreset,
  CaptionPreset,
  RenderPreset,
  ScoringPreset,
  DashboardOverview,
  ProfilePerformance,
  HookTypeStat,
  ClipLengthStat,
  AnalyticsPoint,
  ActivityItem,
} from "../types/clipz";

// --- Helpers ---
const now = new Date();
const iso = (offsetDays = 0, offsetHours = 0) => {
  const d = new Date(now);
  d.setDate(d.getDate() + offsetDays);
  d.setHours(d.getHours() + offsetHours);
  return d.toISOString();
};

// ============================================================
// PROFILES
// ============================================================

export const profiles: Profile[] = [
  {
    id: "1f8e2d6a-7c3b-4e1a-9d5f-2c8a6b4d0e1f",
    name: "Kai Cenat Clips",
    slug: "kai-cenat-clips",
    profile_type: "creator",
    description: "High-energy streamer clips. Focus on reactions, arguments, and surprising moments.",
    avatar_path: "https://picsum.photos/seed/kai-cenat-profile/200/200",
    language: "en",
    status: "active",
    auto_approval_enabled: false,
    default_processing_mode: "balanced",
    default_rights_status: "creator_approved",
    created_by: null,
    created_at: iso(-90),
    updated_at: iso(-7),
    clips_published: 342,
    clips_queued: 18,
  },
  {
    id: "3a9b4c2d-8e5f-4a7a-bc3d-6e1f2a9b7c3d",
    name: "Clip District",
    slug: "clip-district",
    profile_type: "general",
    description: "Multi-creator clip network. Broad content from approved creators.",
    avatar_path: "https://picsum.photos/seed/clip-district/200/200",
    language: "en",
    status: "active",
    auto_approval_enabled: false,
    default_processing_mode: "balanced",
    default_rights_status: "transformative_review",
    created_by: null,
    created_at: iso(-180),
    updated_at: iso(-2),
    clips_published: 1247,
    clips_queued: 47,
  },
  {
    id: "5c8d7e6f-1a2b-4c3d-8e5f-6a7b8c9d0e1f",
    name: "Tech Insights Daily",
    slug: "tech-insights-daily",
    profile_type: "topic",
    description: "Technology commentary, product reviews, and industry analysis clips.",
    avatar_path: "https://picsum.photos/seed/tech-insights/200/200",
    language: "en",
    status: "active",
    auto_approval_enabled: true,
    default_processing_mode: "quality",
    default_rights_status: "licensed",
    created_by: null,
    created_at: iso(-60),
    updated_at: iso(-1),
    clips_published: 156,
    clips_queued: 9,
  },
  {
    id: "7b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e",
    name: "Comedy Hub",
    slug: "comedy-hub",
    profile_type: "topic",
    description: "Stand-up clips, podcast comedy moments, and funny interviews.",
    avatar_path: "https://picsum.photos/seed/comedy-hub/200/200",
    language: "en",
    status: "active",
    auto_approval_enabled: false,
    default_processing_mode: "balanced",
    default_rights_status: "transformative_review",
    created_by: null,
    created_at: iso(-120),
    updated_at: iso(-5),
    clips_published: 892,
    clips_queued: 23,
  },
  {
    id: "9e0f1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b",
    name: "Manual Uploads",
    slug: "manual-uploads",
    profile_type: "manual",
    description: "Manually curated uploads for personal use.",
    avatar_path: "https://picsum.photos/seed/manual-uploads/200/200",
    language: "en",
    status: "active",
    auto_approval_enabled: false,
    default_processing_mode: "speed",
    default_rights_status: "owned",
    created_by: null,
    created_at: iso(-30),
    updated_at: iso(-1),
    clips_published: 28,
    clips_queued: 3,
  },
  {
    id: "b1c2d3e4-f5a6-b7c8-d9e0-f1a2b3c4d5e6",
    name: "Football Highlights",
    slug: "football-highlights",
    profile_type: "topic",
    description: "Football match highlights, player moments, and tactical breakdowns.",
    avatar_path: "https://picsum.photos/seed/football-highlights/200/200",
    language: "en",
    status: "paused",
    auto_approval_enabled: false,
    default_processing_mode: "balanced",
    default_rights_status: "unknown",
    created_by: null,
    created_at: iso(-45),
    updated_at: iso(-14),
    clips_published: 67,
    clips_queued: 0,
  },
];

export const profilePlatforms: ProfilePlatform[] = [
  { id: "p1-pf-1", profile_id: profiles[0].id, platform: "tiktok", handle: "@kaicenatclips", account_id: "acc_tk_001", is_connected: true, posting_enabled: true, daily_post_limit: 3, timezone: "America/New_York", credentials_reference: "vault://tiktok/kc", created_at: iso(-85), updated_at: iso(-3) },
  { id: "p1-pf-2", profile_id: profiles[0].id, platform: "instagram", handle: "@kaicenat.clips", account_id: "acc_ig_001", is_connected: true, posting_enabled: true, daily_post_limit: 2, timezone: "America/New_York", credentials_reference: "vault://instagram/kc", created_at: iso(-85), updated_at: iso(-3) },
  { id: "p1-pf-3", profile_id: profiles[0].id, platform: "youtube", handle: "KaiCenatClips", account_id: "acc_yt_001", is_connected: true, posting_enabled: true, daily_post_limit: 2, timezone: "America/New_York", credentials_reference: "vault://youtube/kc", created_at: iso(-85), updated_at: iso(-3) },
  { id: "p2-pf-1", profile_id: profiles[1].id, platform: "tiktok", handle: "@clipdistrict", account_id: "acc_tk_002", is_connected: true, posting_enabled: true, daily_post_limit: 5, timezone: "America/Los_Angeles", credentials_reference: "vault://tiktok/cd", created_at: iso(-170), updated_at: iso(-1) },
  { id: "p2-pf-2", profile_id: profiles[1].id, platform: "instagram", handle: "@clipdistrict", account_id: "acc_ig_002", is_connected: true, posting_enabled: true, daily_post_limit: 3, timezone: "America/Los_Angeles", credentials_reference: "vault://instagram/cd", created_at: iso(-170), updated_at: iso(-1) },
  { id: "p3-pf-1", profile_id: profiles[2].id, platform: "tiktok", handle: "@techinsightsdaily", account_id: "acc_tk_003", is_connected: true, posting_enabled: true, daily_post_limit: 2, timezone: "UTC", credentials_reference: "vault://tiktok/ti", created_at: iso(-55), updated_at: iso(-1) },
];

export const profileSources: ProfileSource[] = [
  { id: "p1-ps-1", profile_id: profiles[0].id, source_type: "channel", source_url: "https://youtube.com/@kaicenat", source_name: "Kai Cenat — YouTube", authorization_status: "authorized", watcher_enabled: true, last_checked_at: iso(0, -2), created_at: iso(-85), updated_at: iso(-2) },
  { id: "p1-ps-2", profile_id: profiles[0].id, source_type: "channel", source_url: "https://twitch.tv/kaicenat", source_name: "Kai Cenat — Twitch", authorization_status: "authorized", watcher_enabled: true, last_checked_at: iso(0, -1), created_at: iso(-80), updated_at: iso(-1) },
  { id: "p2-ps-1", profile_id: profiles[1].id, source_type: "folder", source_url: null, source_name: "Dropbox — Content Folder", authorization_status: "authorized", watcher_enabled: true, last_checked_at: iso(0, -3), created_at: iso(-170), updated_at: iso(-3) },
  { id: "p2-ps-2", profile_id: profiles[1].id, source_type: "channel", source_url: "https://youtube.com/@variouscreators", source_name: "Creator Network", authorization_status: "authorized", watcher_enabled: true, last_checked_at: iso(0, -5), created_at: iso(-160), updated_at: iso(-5) },
];

// ============================================================
// SOURCES
// ============================================================

const sourceBase = {
  audio_fingerprint: null,
  visual_fingerprint: null,
  file_hash: null,
  codec: "h264",
  error_code: null,
  error_message: null,
};

export const sources: Source[] = [
  { id: "s1a2b3c4-d5e6-f7a8-b9c0-d1e2f3a4b5c6", profile_id: profiles[0].id, title: "Kai Cenat — Epic Rage Moment Stream", source_type: "channel", original_filename: "kaicenat_rage_moment_2026_07_18.mp4", source_url: "https://youtube.com/watch?v=abc123", local_path: "sources/kai/rage_18.mp4", ...sourceBase, duration_ms: 2 * 3600_000 + 15 * 60_000, width: 1920, height: 1080, frame_rate: 60, file_size_bytes: 4_200_000_000, language: "en", rights_status: "creator_approved", status: "completed", imported_at: iso(-3), created_at: iso(-3), updated_at: iso(-2), thumbnail_path: "https://picsum.photos/seed/clip1/320/180", candidates_count: 12 },
  { id: "s2b3c4d5-e6f7-a8b9-c0d1-e2f3a4b5c6d7", profile_id: profiles[0].id, title: "Kai Cenat — Guest Podcast Episode", source_type: "url", original_filename: "kai_guest_podcast_2026_07_16.mp4", source_url: "https://youtube.com/watch?v=def456", local_path: "sources/kai/podcast_16.mp4", ...sourceBase, duration_ms: 3 * 3600_000 + 40 * 60_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 2_800_000_000, language: "en", rights_status: "creator_approved", status: "completed", imported_at: iso(-5), created_at: iso(-5), updated_at: iso(-4), thumbnail_path: "https://picsum.photos/seed/clip2/320/180", candidates_count: 8 },
  { id: "s3c4d5e6-f7a8-b9c0-d1e2-f3a4b5c6d7e8", profile_id: profiles[1].id, title: "Multi-Creator — Gaming Tournament Finals", source_type: "folder", original_filename: "gaming_tournament_finals.mp4", source_url: null, local_path: "sources/gaming/finals.mp4", ...sourceBase, duration_ms: 4 * 3600_000, width: 2560, height: 1440, frame_rate: 60, file_size_bytes: 8_500_000_000, language: "en", rights_status: "transformative_review", status: "analyzing", imported_at: iso(-1), created_at: iso(-1), updated_at: iso(0, -2), thumbnail_path: "https://picsum.photos/seed/clip3/320/180", candidates_count: 0 },
  { id: "s4d5e6f7-a8b9-c0d1-e2f3-a4b5c6d7e8f9", profile_id: profiles[1].id, title: "Creator Collab — Interview Session", source_type: "upload", original_filename: "collab_interview_morning.mp4", source_url: null, local_path: "sources/collabs/morning_interview.mp4", ...sourceBase, duration_ms: 1 * 3600_000 + 12 * 60_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 1_200_000_000, language: "en", rights_status: "transformative_review", status: "transcribing", imported_at: iso(0, -1), created_at: iso(0, -1), updated_at: iso(0, -0.5), thumbnail_path: "https://picsum.photos/seed/clip4/320/180", candidates_count: 0 },
  { id: "s5e6f7a8-b9c0-d1e2-f3a4-b5c6d7e8f9a0", profile_id: profiles[2].id, title: "Tech Review — New Phone Deep Dive", source_type: "channel", original_filename: "tech_phone_review_2026_07_17.mp4", source_url: "https://youtube.com/watch?v=ghi789", local_path: "sources/tech/phone_review_17.mp4", ...sourceBase, duration_ms: 45 * 60_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 780_000_000, language: "en", rights_status: "licensed", status: "candidates_ready", imported_at: iso(-4), created_at: iso(-4), updated_at: iso(-3), thumbnail_path: "https://picsum.photos/seed/clip5/320/180", candidates_count: 15 },
  { id: "s6f7a8b9-c0d1-e2f3-a4b5-c6d7e8f9a0b1", profile_id: profiles[2].id, title: "Industry Analysis — AI Chip Market", source_type: "upload", original_filename: "ai_chip_market_analysis.mp4", source_url: null, local_path: "sources/tech/ai_chip_analysis.mp4", ...sourceBase, duration_ms: 58 * 60_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 920_000_000, language: "en", rights_status: "licensed", status: "completed", imported_at: iso(-7), created_at: iso(-7), updated_at: iso(-6), thumbnail_path: "https://picsum.photos/seed/clip6/320/180", candidates_count: 11 },
  { id: "s7a8b9c0-d1e2-f3a4-b5c6-d7e8f9a0b1c2", profile_id: profiles[3].id, title: "Stand-Up Special — Comedy Central", source_type: "channel", original_filename: "stand_up_special_comedy.mp4", source_url: "https://youtube.com/watch?v=jkl012", local_path: "sources/comedy/standup_special.mp4", ...sourceBase, duration_ms: 55 * 60_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 1_100_000_000, language: "en", rights_status: "transformative_review", status: "completed", imported_at: iso(-6), created_at: iso(-6), updated_at: iso(-5), thumbnail_path: "https://picsum.photos/seed/clip7/320/180", candidates_count: 9 },
  { id: "s8b9c0d1-e2f3-a4b5-c6d7-e8f9a0b1c2d3", profile_id: profiles[3].id, title: "Podcast — Late Night Comedy Show", source_type: "url", original_filename: "late_night_comedy_pod.mp4", source_url: "https://youtube.com/watch?v=mno345", local_path: "sources/comedy/late_night.mp4", ...sourceBase, duration_ms: 2 * 3600_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 1_800_000_000, language: "en", rights_status: "transformative_review", status: "needs_review", imported_at: iso(-2), created_at: iso(-2), updated_at: iso(-1), thumbnail_path: "https://picsum.photos/seed/clip8/320/180", candidates_count: 14 },
  { id: "s9c0d1e2-f3a4-b5c6-d7e8-f9a0b1c2d3e4", profile_id: profiles[4].id, title: "Personal Vlog — Vacation Footage", source_type: "upload", original_filename: "vacation_vlog_2026_07_15.mp4", source_url: null, local_path: "sources/personal/vacation_15.mp4", ...sourceBase, duration_ms: 22 * 60_000, width: 3840, height: 2160, frame_rate: 60, file_size_bytes: 3_500_000_000, language: "en", rights_status: "owned", status: "completed", imported_at: iso(-6), created_at: iso(-6), updated_at: iso(-5), thumbnail_path: "https://picsum.photos/seed/clip9/320/180", candidates_count: 3 },
  { id: "s0d1e2f3-a4b5-c6d7-e8f9-a0b1c2d3e4f5", profile_id: profiles[1].id, title: "Livestream — Charity Event", source_type: "channel", original_filename: "charity_livestream_12h.mp4", source_url: null, local_path: "sources/events/charity_12h.mp4", ...sourceBase, duration_ms: 12 * 3600_000, width: 1920, height: 1080, frame_rate: 30, file_size_bytes: 12_000_000_000, language: "en", rights_status: "unknown", status: "failed", error_code: "SOURCE_UNREADABLE", error_message: "File appears corrupted after byte 2.3 GB", imported_at: iso(-8), created_at: iso(-8), updated_at: iso(-7), thumbnail_path: "https://picsum.photos/seed/clip10/320/180", candidates_count: 0 },
];

// ============================================================
// CANDIDATES
// ============================================================

const candidateBase = {
  analysis_run_id: "a1b2c3d4-analysis" as any,
  safety_status: "safe" as any,
  transcript_excerpt: "Full transcript excerpt would go here, containing the spoken words from the clip segment with proper timestamps and speaker labels.",
} as const;

function makeCandidate(
  i: number,
  sourceId: string,
  profileId: string,
  overrides: Partial<Candidate> = {}
): Candidate {
  const hooks = [
    "You won't believe what happened next...",
    "This is the greatest moment of my career.",
    "Wait, that's actually insane.",
    "I never thought this would work.",
    "This changed EVERYTHING.",
    "Let me show you something incredible.",
    "Nobody talks about this.",
    "Here's why this matters.",
  ];
  const reasons = [
    "Strong opening hook with immediate tension",
    "High emotional intensity throughout",
    "Unexpected twist at 0:15",
    "Clear narrative arc with payoff",
    "Visually dynamic with strong speaker presence",
  ];
  const seed = 100 + i;
  return {
    id: `c${500 + i}-${sourceId.slice(0, 4)}-${profileId.slice(0, 4)}-cand`,
    source_id: sourceId,
    profile_id: profileId,
    ...candidateBase,
    start_ms: (i * 180 + 30) * 1000,
    end_ms: (i * 180 + 30 + 25 + i * 5) * 1000,
    duration_ms: (25 + i * 5) * 1000,
    title: `Clip ${i + 1} — ${hooks[i % hooks.length].slice(0, 30)}...`,
    hook_text: hooks[i % hooks.length],
    selection_reason: reasons[i % reasons.length],
    overall_score: 55 + ((i * 13) % 40),
    crop_confidence: 0.7 + ((i * 7) % 25) / 100,
    audio_quality_score: 0.75 + ((i * 3) % 20) / 100,
    visual_quality_score: 0.8 + ((i * 5) % 18) / 100,
    duplicate_risk: (i * 11) % 40,
    rights_status: "creator_approved",
    approval_status: i === 0 ? "pending" : i === 1 ? "approved" : i === 2 ? "needs_changes" : i === 3 ? "rejected" : "pending",
    recommended_platform: (["tiktok", "instagram", "youtube", "threads"] as const)[i % 4],
    created_at: iso(-3, -i),
    updated_at: iso(-2, -i),
    thumbnail_path: `https://picsum.photos/seed/cand${seed}/320/180`,
    source_title: sources.find((s) => s.id === sourceId)?.title,
    profile_name: profiles.find((p) => p.id === profileId)?.name,
    score_breakdown: [],
    ...overrides,
  };
}

export const candidates: Candidate[] = [
  makeCandidate(0, sources[0].id, profiles[0].id, { overall_score: 91 }),
  makeCandidate(1, sources[0].id, profiles[0].id, { overall_score: 85, approval_status: "pending" }),
  makeCandidate(2, sources[0].id, profiles[0].id, { overall_score: 78, approval_status: "pending" }),
  makeCandidate(3, sources[0].id, profiles[0].id, { overall_score: 72, approval_status: "approved" }),
  makeCandidate(4, sources[1].id, profiles[0].id, { overall_score: 88 }),
  makeCandidate(5, sources[1].id, profiles[0].id, { overall_score: 67, approval_status: "needs_changes" }),
  makeCandidate(6, sources[4].id, profiles[2].id, { overall_score: 82 }),
  makeCandidate(7, sources[4].id, profiles[2].id, { overall_score: 79 }),
  makeCandidate(8, sources[4].id, profiles[2].id, { overall_score: 66, approval_status: "rejected" }),
  makeCandidate(9, sources[6].id, profiles[3].id, { overall_score: 84 }),
  makeCandidate(10, sources[7].id, profiles[3].id, { overall_score: 76 }),
  makeCandidate(11, sources[8].id, profiles[4].id, { overall_score: 59 }),
];

// Add score breakdowns
export const candidateScores: CandidateScore[] = [];
candidates.forEach((c) => {
  const signals: { name: any; raw: number; norm: number; weight: number }[] = [
    { name: "hook_strength", raw: 70 + Math.random() * 25, norm: 0.7 + Math.random() * 0.25, weight: 0.2 },
    { name: "emotional_intensity", raw: 60 + Math.random() * 30, norm: 0.6 + Math.random() * 0.3, weight: 0.15 },
    { name: "profile_match", raw: 65 + Math.random() * 30, norm: 0.65 + Math.random() * 0.3, weight: 0.18 },
    { name: "payoff_strength", raw: 50 + Math.random() * 40, norm: 0.5 + Math.random() * 0.4, weight: 0.12 },
    { name: "novelty", raw: 40 + Math.random() * 45, norm: 0.4 + Math.random() * 0.45, weight: 0.1 },
    { name: "visual_activity", raw: 55 + Math.random() * 35, norm: 0.55 + Math.random() * 0.35, weight: 0.08 },
    { name: "length_fit", raw: 70 + Math.random() * 25, norm: 0.7 + Math.random() * 0.25, weight: 0.07 },
    { name: "context_completeness", raw: 60 + Math.random() * 30, norm: 0.6 + Math.random() * 0.3, weight: 0.1 },
  ];
  signals.forEach((s, idx) => {
    candidateScores.push({
      id: `sc-${c.id.slice(0, 8)}-${idx}`,
      candidate_id: c.id,
      signal_name: s.name,
      raw_value: s.raw,
      normalized_value: s.norm,
      weight: s.weight,
      weighted_score: s.norm * s.weight * 100,
      explanation: `${s.name.replace("_", " ")} — signal strength based on model analysis`,
      created_at: c.created_at,
    });
  });
});
// Attach score arrays to candidates for convenience
candidates.forEach((c) => {
  c.score_breakdown = candidateScores.filter((sc) => sc.candidate_id === c.id);
});

// ============================================================
// JOBS
// ============================================================

export const jobs: Job[] = [
  { id: "j1-render-1a2b", job_type: "render_clip", entity_type: "candidate", entity_id: candidates[0].id, profile_id: profiles[0].id, priority: "high", status: "running", progress_percent: 67, attempts: 1, max_attempts: 3, retryable: true, locked_by: "worker-01", locked_at: iso(0, -0.3), started_at: iso(0, -0.5), completed_at: null, error_code: null, error_message: null, payload_json: { render_preset: "tiktok_vertical" }, result_json: null, created_at: iso(0, -1), updated_at: iso(0, -0.2), entity_title: candidates[0].title, profile_name: profiles[0].name, render_device: "GPU (RTX 4080)", render_preset: "TikTok Vertical", estimated_time: "2m 14s" },
  { id: "j2-render-3c4d", job_type: "render_clip", entity_type: "candidate", entity_id: candidates[4].id, profile_id: profiles[0].id, priority: "normal", status: "running", progress_percent: 34, attempts: 1, max_attempts: 3, retryable: true, locked_by: "worker-02", locked_at: iso(0, -0.1), started_at: iso(0, -0.3), completed_at: null, error_code: null, error_message: null, payload_json: { render_preset: "tiktok_vertical" }, result_json: null, created_at: iso(0, -0.7), updated_at: iso(0, -0.1), entity_title: candidates[4].title, profile_name: profiles[0].name, render_device: "GPU (RTX 4080)", render_preset: "Instagram Reel", estimated_time: "5m 30s" },
  { id: "j3-render-5e6f", job_type: "render_clip", entity_type: "candidate", entity_id: candidates[6].id, profile_id: profiles[2].id, priority: "low", status: "queued", progress_percent: 0, attempts: 0, max_attempts: 3, retryable: true, locked_by: null, locked_at: null, started_at: null, completed_at: null, error_code: null, error_message: null, payload_json: { render_preset: "youtube_shorts" }, result_json: null, created_at: iso(0, -0.1), updated_at: iso(0, -0.1), entity_title: candidates[6].title, profile_name: profiles[2].name, render_device: "CPU", render_preset: "YouTube Shorts", estimated_time: "8m 10s" },
  { id: "j4-transcribe-7g8h", job_type: "transcribe", entity_type: "source", entity_id: sources[3].id, profile_id: profiles[1].id, priority: "normal", status: "running", progress_percent: 78, attempts: 1, max_attempts: 3, retryable: true, locked_by: "worker-02", locked_at: iso(0, -0.2), started_at: iso(0, -0.4), completed_at: null, error_code: null, error_message: null, payload_json: { model: "large-v3", language: "en" }, result_json: null, created_at: iso(0, -0.5), updated_at: iso(0, -0.1), entity_title: sources[3].title, profile_name: profiles[1].name, estimated_time: "6m 45s" },
  { id: "j5-analyze-9i0j", job_type: "analyze_source", entity_type: "source", entity_id: sources[2].id, profile_id: profiles[1].id, priority: "high", status: "running", progress_percent: 45, attempts: 1, max_attempts: 3, retryable: true, locked_by: "worker-01", locked_at: iso(0, -0.2), started_at: iso(0, -0.6), completed_at: null, error_code: null, error_message: null, payload_json: { scoring_preset: "default_v2" }, result_json: null, created_at: iso(0, -0.7), updated_at: iso(0, -0.15), entity_title: sources[2].title, profile_name: profiles[1].name, estimated_time: "12m 00s" },
  { id: "j6-render-k1l2", job_type: "render_clip", entity_type: "candidate", entity_id: candidates[9].id, profile_id: profiles[3].id, priority: "normal", status: "completed", progress_percent: 100, attempts: 1, max_attempts: 3, retryable: true, locked_by: null, locked_at: null, started_at: iso(-1, -4), completed_at: iso(-1, -3.8), error_code: null, error_message: null, payload_json: { render_preset: "tiktok_vertical" }, result_json: { output_path: "renders/j6/final.mp4" }, created_at: iso(-1, -5), updated_at: iso(-1, -3.8), entity_title: candidates[9].title, profile_name: profiles[3].name, render_device: "GPU (RTX 4080)", render_preset: "TikTok Vertical", estimated_time: "3m 20s", output_size: 28_000_000  },
  { id: "j7-render-m3n4", job_type: "render_clip", entity_type: "candidate", entity_id: "c-failed-001", profile_id: profiles[1].id, priority: "high", status: "failed", progress_percent: 42, attempts: 3, max_attempts: 3, retryable: false, locked_by: null, locked_at: null, started_at: iso(-2, -2), completed_at: iso(-2, -1.8), error_code: "RENDER_GPU_UNAVAILABLE", error_message: "GPU memory allocation failed at 42%. Candidate resolution exceeds available GPU VRAM. Consider lowering render quality or using CPU fallback.", payload_json: { render_preset: "high_quality" }, result_json: null, created_at: iso(-2, -3), updated_at: iso(-2, -1.8), entity_title: "Failed clip — high res footage", profile_name: profiles[1].name, render_device: "GPU (RTX 4080)", render_preset: "High Quality", estimated_time: "failed" },
  { id: "j8-export-o5p6", job_type: "build_export", entity_type: "render", entity_id: "ro-completed-001", profile_id: profiles[0].id, priority: "normal", status: "queued", progress_percent: 0, attempts: 0, max_attempts: 3, retryable: true, locked_by: null, locked_at: null, started_at: null, completed_at: null, error_code: null, error_message: null, payload_json: { platforms: ["tiktok", "instagram", "youtube"] }, result_json: null, created_at: iso(0, -0.05), updated_at: iso(0, -0.05), entity_title: "Export package — Epic Rage", profile_name: profiles[0].name, estimated_time: "1m 10s" },
];

// ============================================================
// SCHEDULES
// ============================================================

export const schedules: Schedule[] = [
  { id: "sch-001", profile_id: profiles[0].id, render_output_id: "ro-001", candidate_id: candidates[3].id, platform: "tiktok", scheduled_for: iso(0, 4).slice(0, 16) + ":00Z", timezone: "America/New_York", status: "scheduled", priority: "normal", notes: null, created_at: iso(-1), updated_at: iso(-1), clip_title: candidates[3].title, thumbnail_path: candidates[3].thumbnail_path, profile_name: profiles[0].name },
  { id: "sch-002", profile_id: profiles[0].id, render_output_id: "ro-002", candidate_id: candidates[1].id, platform: "instagram", scheduled_for: iso(0, 8).slice(0, 16) + ":00Z", timezone: "America/New_York", status: "scheduled", priority: "high", notes: "Viral potential — push to story", created_at: iso(-1), updated_at: iso(-1), clip_title: candidates[1].title, thumbnail_path: candidates[1].thumbnail_path, profile_name: profiles[0].name },
  { id: "sch-003", profile_id: profiles[1].id, render_output_id: "ro-003", candidate_id: candidates[9].id, platform: "youtube", scheduled_for: iso(1, 12).slice(0, 16) + ":00Z", timezone: "America/Los_Angeles", status: "scheduled", priority: "normal", notes: null, created_at: iso(-1), updated_at: iso(-1), clip_title: candidates[9].title, thumbnail_path: candidates[9].thumbnail_path, profile_name: profiles[1].name },
  { id: "sch-004", profile_id: profiles[2].id, render_output_id: "ro-004", candidate_id: candidates[6].id, platform: "tiktok", scheduled_for: iso(1, 18).slice(0, 16) + ":00Z", timezone: "UTC", status: "draft", priority: "normal", notes: "Awaiting approval", created_at: iso(0, -0.5), updated_at: iso(0, -0.5), clip_title: candidates[6].title, thumbnail_path: candidates[6].thumbnail_path, profile_name: profiles[2].name },
  { id: "sch-005", profile_id: profiles[0].id, render_output_id: "ro-005", candidate_id: candidates[4].id, platform: "threads", scheduled_for: iso(2, 10).slice(0, 16) + ":00Z", timezone: "America/New_York", status: "scheduled", priority: "low", notes: null, created_at: iso(0, -0.3), updated_at: iso(0, -0.3), clip_title: candidates[4].title, thumbnail_path: candidates[4].thumbnail_path, profile_name: profiles[0].name },
  { id: "sch-006", profile_id: profiles[3].id, render_output_id: "ro-006", candidate_id: candidates[10].id, platform: "tiktok", scheduled_for: iso(2, 14).slice(0, 16) + ":00Z", timezone: "America/Chicago", status: "scheduled", priority: "normal", notes: null, created_at: iso(0, -0.2), updated_at: iso(0, -0.2), clip_title: candidates[10].title, thumbnail_path: candidates[10].thumbnail_path, profile_name: profiles[3].name },
  { id: "sch-007", profile_id: profiles[4].id, render_output_id: "ro-007", candidate_id: candidates[11].id, platform: "instagram", scheduled_for: iso(3, 16).slice(0, 16) + ":00Z", timezone: "UTC", status: "ready", priority: "normal", notes: null, created_at: iso(-2), updated_at: iso(-1), clip_title: candidates[11].title, thumbnail_path: candidates[11].thumbnail_path, profile_name: profiles[4].name },
  { id: "sch-008", profile_id: profiles[1].id, render_output_id: "ro-008", candidate_id: null, platform: "tiktok", scheduled_for: iso(-1, 6).slice(0, 16) + ":00Z", timezone: "America/Los_Angeles", status: "published", priority: "normal", notes: null, created_at: iso(-3), updated_at: iso(-1), clip_title: "Yesterday's top clip", thumbnail_path: "https://picsum.photos/seed/sch8/320/180", profile_name: profiles[1].name },
  { id: "sch-009", profile_id: profiles[0].id, render_output_id: "ro-009", candidate_id: null, platform: "youtube", scheduled_for: iso(-2, 12).slice(0, 16) + ":00Z", timezone: "America/New_York", status: "published", priority: "high", notes: null, created_at: iso(-4), updated_at: iso(-2), clip_title: "Mid-week highlight", thumbnail_path: "https://picsum.photos/seed/sch9/320/180", profile_name: profiles[0].name },
  { id: "sch-010", profile_id: profiles[2].id, render_output_id: "ro-010", candidate_id: null, platform: "tiktok", scheduled_for: iso(-3, 14).slice(0, 16) + ":00Z", timezone: "UTC", status: "failed", priority: "normal", notes: "Auth token expired", created_at: iso(-5), updated_at: iso(-3), clip_title: "Tech news flash", thumbnail_path: "https://picsum.photos/seed/sch10/320/180", profile_name: profiles[2].name },
];

// ============================================================
// PRESETS
// ============================================================

export const brandingPresets: BrandingPreset[] = [
  { id: "bp-kc-01", profile_id: profiles[0].id, name: "Kai Cenat Standard", version: 3, is_active: true, logo_path: "branding/kc_logo.png", watermark: true, watermark_position: "bottom-right", outro_duration_ms: 3000, color_primary: "#FF0000", color_secondary: "#000000", created_at: iso(-60) },
  { id: "bp-cd-01", profile_id: profiles[1].id, name: "Clip District", version: 5, is_active: true, logo_path: "branding/cd_logo.png", watermark: true, watermark_position: "top-left", outro_duration_ms: 2000, color_primary: "#7c5cff", color_secondary: "#22d3ee", created_at: iso(-120) },
];

export const captionPresets: CaptionPreset[] = [
  { id: "cp-tk-bold-01", profile_id: profiles[0].id, name: "TikTok Bold", version: 2, is_active: true, font_family: "Inter Black", font_size: 48, font_color: "#FFFFFF", stroke_color: "#000000", stroke_width: 4, background_enabled: false, background_color: "#000000", background_opacity: 0, position: "bottom", max_lines: 2, highlight_enabled: true, highlight_color: "#FFE600", created_at: iso(-80) },
  { id: "cp-yt-clean-01", profile_id: profiles[2].id, name: "YouTube Clean", version: 1, is_active: true, font_family: "Inter SemiBold", font_size: 36, font_color: "#FFFFFF", stroke_color: "rgba(0,0,0,0.7)", stroke_width: 2, background_enabled: true, background_color: "#000000", background_opacity: 0.4, position: "bottom", max_lines: 2, highlight_enabled: false, highlight_color: "#22d3ee", created_at: iso(-50) },
];

export const renderPresets: RenderPreset[] = [
  { id: "rp-tk-vert-01", profile_id: profiles[0].id, name: "TikTok Vertical", version: 3, is_active: true, resolution: "1080x1920", aspect_ratio: "9:16", frame_rate: 30, codec: "h264", bitrate_kbps: 8000, audio_codec: "aac", audio_bitrate_kbps: 192, crop_strategy: "auto", enhancement_mode: "standard", platform_target: "tiktok", created_at: iso(-80) },
  { id: "rp-ig-reel-01", profile_id: profiles[0].id, name: "Instagram Reel", version: 2, is_active: true, resolution: "1080x1920", aspect_ratio: "9:16", frame_rate: 30, codec: "h264", bitrate_kbps: 7000, audio_codec: "aac", audio_bitrate_kbps: 160, crop_strategy: "center", enhancement_mode: "light", platform_target: "instagram", created_at: iso(-75) },
  { id: "rp-yt-short-01", profile_id: profiles[2].id, name: "YouTube Shorts", version: 2, is_active: true, resolution: "1080x1920", aspect_ratio: "9:16", frame_rate: 30, codec: "h264", bitrate_kbps: 10000, audio_codec: "aac", audio_bitrate_kbps: 256, crop_strategy: "auto", enhancement_mode: "high", platform_target: "youtube", created_at: iso(-40) },
];

export const scoringPresets: ScoringPreset[] = [
  { id: "sp-default-01", profile_id: profiles[0].id, name: "Default v2", version: 2, is_active: true, weights_json: { hook_strength: 0.2, emotional_intensity: 0.15, profile_match: 0.18, payoff_strength: 0.12, novelty: 0.1, visual_activity: 0.08, length_fit: 0.07, context_completeness: 0.1 }, thresholds_json: { min_overall_score: 50, duplicate_risk_max: 50 }, created_at: iso(-100) },
  { id: "sp-tech-01", profile_id: profiles[2].id, name: "Tech Focus", version: 1, is_active: true, weights_json: { hook_strength: 0.15, context_completeness: 0.25, profile_match: 0.15, payoff_strength: 0.1, novelty: 0.15, visual_activity: 0.05, length_fit: 0.1, emotional_intensity: 0.05 }, thresholds_json: { min_overall_score: 45, duplicate_risk_max: 60 }, created_at: iso(-50) },
];

// ============================================================
// NOTIFICATIONS
// ============================================================

export const notifications: Notification[] = [
  { id: "notif-001", user_id: null, type: "action_required", title: "Candidates ready for review", message: "14 new candidates from 'Late Night Comedy' need your review.", entity_type: "source", entity_id: sources[7].id, is_read: false, created_at: iso(-1) },
  { id: "notif-002", user_id: null, type: "success", title: "Render complete", message: "'Clip 1 — You won't believe...' has finished rendering.", entity_type: "candidate", entity_id: candidates[0].id, is_read: false, created_at: iso(0, -0.5) },
  { id: "notif-003", user_id: null, type: "error", title: "Render failed", message: "Render job j7 failed: GPU memory allocation failed.", entity_type: "candidate", entity_id: "c-failed-001", is_read: false, created_at: iso(-2) },
  { id: "notif-004", user_id: null, type: "warning", title: "Storage nearly full", message: "Storage is at 74%. Consider archiving old sources.", entity_type: null, entity_id: null, is_read: true, created_at: iso(-3) },
  { id: "notif-005", user_id: null, type: "informational", title: "Processing complete", message: "'AI Chip Market Analysis' — 11 candidates generated.", entity_type: "source", entity_id: sources[5].id, is_read: true, created_at: iso(-6) },
];

// ============================================================
// ANALYTICS DATA POINTS
// ============================================================

export const analyticsData: AnalyticsPoint[] = Array.from({ length: 14 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() - (13 - i));
  const dateStr = d.toISOString().split("T")[0];
  const base = 20000 + i * 3000;
  const variance = Math.sin(i * 1.5) * 15000;
  const views = Math.max(0, base + variance + i * 2000);
  return {
    date: dateStr,
    views: Math.round(views),
    likes: Math.round(views * 0.07),
    comments: Math.round(views * 0.012),
    shares: Math.round(views * 0.008),
    clips_posted: 1 + (i % 3),
  };
});

export const hookTypeStats: HookTypeStat[] = [
  { type: "Mystery Hook", count: 47, avg_views: 128000, avg_completion: 0.68 },
  { type: "Shock / Surprise", count: 38, avg_views: 96000, avg_completion: 0.59 },
  { type: "Direct Challenge", count: 29, avg_views: 82000, avg_completion: 0.62 },
  { type: "Problem / Solution", count: 52, avg_views: 74000, avg_completion: 0.71 },
  { type: "Story Opener", count: 61, avg_views: 68000, avg_completion: 0.64 },
  { type: "Visual Hook", count: 33, avg_views: 112000, avg_completion: 0.55 },
];

export const clipLengthStats: ClipLengthStat[] = [
  { length: "0-15s", count: 28, avg_views: 92000, avg_completion: 0.78 },
  { length: "15-30s", count: 54, avg_views: 115000, avg_completion: 0.66 },
  { length: "30-45s", count: 37, avg_views: 78000, avg_completion: 0.58 },
  { length: "45-60s", count: 19, avg_views: 54000, avg_completion: 0.48 },
  { length: "60-90s", count: 8, avg_views: 38000, avg_completion: 0.41 },
];

export const profilePerformance: ProfilePerformance[] = profiles
  .filter((p) => p.status === "active")
  .map((p, i) => ({
    profile_id: p.id,
    profile_name: p.name,
    clips_count: p.clips_published || 0,
    total_views: (p.clips_published || 0) * 45000 + i * 100000,
    engagement_rate: 6 + i * 1.2,
    completion_rate: 45 + i * 5,
    avg_score: 72 + i * 3,
  }));

// ============================================================
// DASHBOARD OVERVIEW (composite)
// ============================================================

export const recentActivity: ActivityItem[] = [
  { id: "act-001", type: "candidate.created", message: "12 candidates generated from Epic Rage stream", entity_type: "source", entity_id: sources[0].id, timestamp: iso(-2) },
  { id: "act-002", type: "render.completed", message: "Clip 1 rendered successfully (28 MB)", entity_type: "candidate", entity_id: candidates[0].id, timestamp: iso(-1, -4) },
  { id: "act-003", type: "source.imported", message: "New source uploaded: collab_interview_morning.mp4", entity_type: "source", entity_id: sources[3].id, timestamp: iso(0, -1) },
  { id: "act-004", type: "profile.created", message: "Manual Uploads profile created", entity_type: "profile", entity_id: profiles[4].id, timestamp: iso(-30) },
  { id: "act-005", type: "schedule.scheduled", message: "3 posts scheduled for this week", entity_type: "schedule", entity_id: schedules[0].id, timestamp: iso(-1) },
];

export const dashboardOverview: DashboardOverview = {
  active_profile_count: profiles.filter((p) => p.status === "active").length,
  sources_processing: sources.filter((s) => s.status === "transcribing" || s.status === "analyzing").length,
  candidates_awaiting_review: candidates.filter((c) => c.approval_status === "pending").length,
  active_render_jobs: jobs.filter((j) => j.status === "running" && j.job_type === "render_clip").length,
  scheduled_posts: schedules.filter((s) => s.status === "scheduled" || s.status === "ready").length,
  failed_jobs: jobs.filter((j) => j.status === "failed").length,
  storage_utilization_bytes: 342_000_000_000,
  storage_total_bytes: 1_000_000_000_000,
  worker_health: {
    api: true,
    database: true,
    worker: true,
    ffmpeg: true,
    transcription: true,
    storage: true,
  },
  recent_activity: recentActivity,
  recent_analytics: {
    total_views_7d: 847230,
    total_engagement_7d: 67778,
    completion_rate_avg: 0.61,
    views_change_percent: 12.4,
  },
  top_hook_types: hookTypeStats,
  chart_data: analyticsData,
  upcoming_schedules: schedules.filter((s) => s.status === "scheduled" || s.status === "ready").slice(0, 6),
};
