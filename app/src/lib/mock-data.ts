// Mock data for CLIPZ dashboard simulation

export type ProfileType = "general" | "creator" | "topic" | "manual";

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
  status: "active" | "paused" | "draft";
  rightsStatus: string;
  autoApproval: boolean;
  safetyLevel: string;
  postingSchedule: Record<string, number>;
}

export type SourceStatus =
  | "validating"
  | "queued"
  | "transcribing"
  | "analyzing"
  | "candidates_ready"
  | "processed"
  | "failed";

export interface SourceVideo {
  id: string;
  profileId: string;
  title: string;
  sourceUrl: string;
  sourceType: "upload" | "url" | "folder" | "channel";
  filename: string;
  duration: number; // seconds
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

export interface AnalyticsPoint {
  date: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  clipsPosted: number;
}

export interface HookTypeStat {
  type: string;
  count: number;
  avgViews: number;
  avgCompletion: number;
}

export interface ClipLengthStat {
  length: string;
  count: number;
  avgViews: number;
  avgCompletion: number;
}

// ========== PROFILES ==========
export const profiles: Profile[] = [
  {
    id: "p1",
    name: "Kai Cenat Clips",
    type: "creator",
    description: "High-energy streamer clips. Focus on reactions, arguments, and surprising moments.",
    image: "https://picsum.photos/seed/kai-cenat-profile/200/200",
    sourceChannels: ["YouTube", "Twitch"],
    targetPlatforms: ["TikTok", "Instagram", "YouTube Shorts", "Threads"],
    clipLengths: { min: 20, max: 45 },
    contentThemes: ["High-energy", "Funny reactions", "Arguments", "Surprising moments"],
    clipsPublished: 342,
    clipsQueued: 18,
    status: "active",
    rightsStatus: "creator-approved",
    autoApproval: false,
    safetyLevel: "moderate",
    postingSchedule: { TikTok: 3, Instagram: 2, "YouTube Shorts": 2, Threads: 1 },
  },
  {
    id: "p2",
    name: "Clip District",
    type: "general",
    description: "Multi-creator clip network. Broad content from approved creators.",
    image: "https://picsum.photos/seed/clip-district/200/200",
    sourceChannels: ["YouTube", "Twitch", "Kick", "Manual uploads"],
    targetPlatforms: ["TikTok", "Instagram", "YouTube Shorts"],
    clipLengths: { min: 15, max: 60 },
    contentThemes: ["Gaming", "Comedy", "Reactions", "Interviews"],
    clipsPublished: 1247,
    clipsQueued: 47,
    status: "active",
    rightsStatus: "transformative-review",
    autoApproval: false,
    safetyLevel: "high",
    postingSchedule: { TikTok: 5, Instagram: 3, "YouTube Shorts": 3 },
  },
  {
    id: "p3",
    name: "Tech Insights Daily",
    type: "topic",
    description: "Technology commentary, product reviews, and industry analysis clips.",
    image: "https://picsum.photos/seed/tech-insights/200/200",
    sourceChannels: ["YouTube", "Podcast feeds"],
    targetPlatforms: ["TikTok", "YouTube Shorts", "Threads", "X"],
    clipLengths: { min: 25, max: 90 },
    contentThemes: ["Product reviews", "Industry analysis", "Debates", "Tech news"],
    clipsPublished: 156,
    clipsQueued: 9,
    status: "active",
    rightsStatus: "licensed",
    autoApproval: true,
    safetyLevel: "low",
    postingSchedule: { TikTok: 2, "YouTube Shorts": 2, Threads: 1, X: 2 },
  },
  {
    id: "p4",
    name: "Comedy Hub",
    type: "topic",
    description: "Stand-up clips, podcast comedy moments, and funny interviews.",
    image: "https://picsum.photos/seed/comedy-hub/200/200",
    sourceChannels: ["YouTube", "Spotify video"],
    targetPlatforms: ["TikTok", "Instagram", "YouTube Shorts"],
    clipLengths: { min: 15, max: 45 },
    contentThemes: ["Stand-up", "Podcast comedy", "Funny stories", "Roasts"],
    clipsPublished: 892,
    clipsQueued: 23,
    status: "active",
    rightsStatus: "transformative-review",
    autoApproval: false,
    safetyLevel: "moderate",
    postingSchedule: { TikTok: 4, Instagram: 2, "YouTube Shorts": 2 },
  },
  {
    id: "p5",
    name: "Manual - Quick Uploads",
    type: "manual",
    description: "Direct upload channel for manually selected videos and raw cuts.",
    image: "https://picsum.photos/seed/manual-uploads/200/200",
    sourceChannels: ["Manual upload only"],
    targetPlatforms: ["TikTok", "Instagram"],
    clipLengths: { min: 10, max: 120 },
    contentThemes: ["Mixed"],
    clipsPublished: 28,
    clipsQueued: 3,
    status: "paused",
    rightsStatus: "owned",
    autoApproval: true,
    safetyLevel: "low",
    postingSchedule: { TikTok: 1, Instagram: 1 },
  },
  {
    id: "p6",
    name: "Football Highlights",
    type: "topic",
    description: "Football match moments, player reactions, and analysis clips.",
    image: "https://picsum.photos/seed/football-highlights/200/200",
    sourceChannels: ["YouTube", "Match footage"],
    targetPlatforms: ["TikTok", "Instagram", "YouTube Shorts", "X"],
    clipLengths: { min: 20, max: 60 },
    contentThemes: ["Goals", "Reactions", "Controversies", "Analysis"],
    clipsPublished: 0,
    clipsQueued: 0,
    status: "draft",
    rightsStatus: "unknown",
    autoApproval: false,
    safetyLevel: "moderate",
    postingSchedule: { TikTok: 3, Instagram: 1, "YouTube Shorts": 2, X: 2 },
  },
];

// ========== SOURCE VIDEOS ==========
export const sourceVideos: SourceVideo[] = [
  {
    id: "s1",
    profileId: "p1",
    title: "Kai Cenat - IRL Stream NYC Day 47",
    sourceUrl: "https://youtube.com/watch?v=example1",
    sourceType: "channel",
    filename: "kai_nyc_day47.mp4",
    duration: 14520,
    resolution: "1920x1080",
    fps: 60,
    fileSize: "8.2 GB",
    dateAdded: "2024-03-15T09:23:00Z",
    status: "candidates_ready",
    progress: 100,
    rightsStatus: "creator-approved",
    duplicateStatus: "unique",
    candidatesFound: 12,
    thumbnail: "https://picsum.photos/seed/kai-stream1/320/180",
  },
  {
    id: "s2",
    profileId: "p1",
    title: "Kai Cenat - GTA RP Season 3 Finale",
    sourceUrl: "https://twitch.tv/videos/example2",
    sourceType: "channel",
    filename: "kai_gta_rp_s3_finale.mp4",
    duration: 21600,
    resolution: "1920x1080",
    fps: 60,
    fileSize: "12.4 GB",
    dateAdded: "2024-03-14T22:15:00Z",
    status: "analyzing",
    progress: 68,
    rightsStatus: "creator-approved",
    duplicateStatus: "unique",
    candidatesFound: 0,
    thumbnail: "https://picsum.photos/seed/kai-gta/320/180",
  },
  {
    id: "s3",
    profileId: "p2",
    title: "Multiple Creators - Best of Week 12 Compilation",
    sourceUrl: "",
    sourceType: "upload",
    filename: "best_of_week12_raw.mp4",
    duration: 7200,
    resolution: "1920x1080",
    fps: 30,
    fileSize: "3.8 GB",
    dateAdded: "2024-03-15T11:42:00Z",
    status: "transcribing",
    progress: 42,
    rightsStatus: "transformative-review",
    duplicateStatus: "near_duplicate",
    candidatesFound: 0,
    thumbnail: "https://picsum.photos/seed/best-of-week12/320/180",
  },
  {
    id: "s4",
    profileId: "p3",
    title: "Tech Podcast Ep 142 - AI Regulation Debate",
    sourceUrl: "https://youtube.com/watch?v=example4",
    sourceType: "url",
    filename: "tech_podcast_ep142.mp4",
    duration: 5400,
    resolution: "1920x1080",
    fps: 30,
    fileSize: "2.1 GB",
    dateAdded: "2024-03-15T08:00:00Z",
    status: "processed",
    progress: 100,
    rightsStatus: "licensed",
    duplicateStatus: "unique",
    candidatesFound: 7,
    thumbnail: "https://picsum.photos/seed/tech-podcast-142/320/180",
  },
  {
    id: "s5",
    profileId: "p4",
    title: "Stand-Up Special - Live at the Comedy Cellar",
    sourceUrl: "",
    sourceType: "upload",
    filename: "comedy_cellar_live.mp4",
    duration: 3600,
    resolution: "1920x1080",
    fps: 24,
    fileSize: "2.7 GB",
    dateAdded: "2024-03-15T06:30:00Z",
    status: "candidates_ready",
    progress: 100,
    rightsStatus: "licensed",
    duplicateStatus: "unique",
    candidatesFound: 15,
    thumbnail: "https://picsum.photos/seed/comedy-cellar/320/180",
  },
  {
    id: "s6",
    profileId: "p2",
    title: "Creator Collab Stream - 24hr Charity Event",
    sourceUrl: "https://youtube.com/watch?v=example6",
    sourceType: "url",
    filename: "charity_stream_24hr.mp4",
    duration: 86400,
    resolution: "1920x1080",
    fps: 30,
    fileSize: "32.0 GB",
    dateAdded: "2024-03-14T20:00:00Z",
    status: "queued",
    progress: 0,
    rightsStatus: "creator-approved",
    duplicateStatus: "unique",
    candidatesFound: 0,
    thumbnail: "https://picsum.photos/seed/charity-stream/320/180",
  },
  {
    id: "s7",
    profileId: "p3",
    title: "Phone Review - Top 5 Smartphones 2024",
    sourceUrl: "https://youtube.com/watch?v=example7",
    sourceType: "channel",
    filename: "phone_review_top5_2024.mp4",
    duration: 1800,
    resolution: "3840x2160",
    fps: 30,
    fileSize: "4.5 GB",
    dateAdded: "2024-03-15T10:15:00Z",
    status: "validating",
    progress: 15,
    rightsStatus: "licensed",
    duplicateStatus: "unique",
    candidatesFound: 0,
    thumbnail: "https://picsum.photos/seed/phone-review-2024/320/180",
  },
  {
    id: "s8",
    profileId: "p4",
    title: "Podcast Episode 287 - The Funny One",
    sourceUrl: "https://youtube.com/watch?v=example8",
    sourceType: "channel",
    filename: "podcast_ep287_funny.mp4",
    duration: 4200,
    resolution: "1920x1080",
    fps: 30,
    fileSize: "1.8 GB",
    dateAdded: "2024-03-14T15:30:00Z",
    status: "processed",
    progress: 100,
    rightsStatus: "transformative-review",
    duplicateStatus: "unique",
    candidatesFound: 9,
    thumbnail: "https://picsum.photos/seed/podcast-ep287/320/180",
  },
  {
    id: "s9",
    profileId: "p1",
    title: "Kai Reacts to Viral Videos - Vol 3",
    sourceUrl: "https://youtube.com/watch?v=example9",
    sourceType: "channel",
    filename: "kai_reacts_viral_vol3.mp4",
    duration: 2700,
    resolution: "1920x1080",
    fps: 60,
    fileSize: "2.2 GB",
    dateAdded: "2024-03-13T14:00:00Z",
    status: "failed",
    progress: 35,
    rightsStatus: "creator-approved",
    duplicateStatus: "unique",
    candidatesFound: 0,
    thumbnail: "https://picsum.photos/seed/kai-reacts-vol3/320/180",
  },
  {
    id: "s10",
    profileId: "p5",
    title: "Client Upload - Brand Deal Raw Footage",
    sourceUrl: "",
    sourceType: "upload",
    filename: "brand_deal_raw_v2.mp4",
    duration: 900,
    resolution: "1920x1080",
    fps: 30,
    fileSize: "890 MB",
    dateAdded: "2024-03-15T12:00:00Z",
    status: "candidates_ready",
    progress: 100,
    rightsStatus: "owned",
    duplicateStatus: "unique",
    candidatesFound: 4,
    thumbnail: "https://picsum.photos/seed/brand-deal-raw/320/180",
  },
];

// ========== CANDIDATE CLIPS ==========
export const candidateClips: CandidateClip[] = [
  {
    id: "c1",
    sourceId: "s1",
    profileId: "p1",
    score: 91,
    scoreBreakdown: {
      hook: 18,
      context: 14,
      emotion: 15,
      profileMatch: 14,
      quote: 9,
      visual: 9,
      topic: 5,
      length: 4,
      novelty: 3,
    },
    startTime: 234.5,
    endTime: 267.2,
    duration: 32.7,
    hook: "\"He actually did it. I cannot believe he actually did it.\"",
    title: "The most chaotic moment of the stream",
    transcript: "You are not going to believe what just happened. Wait, wait, hold on. He actually did it. I cannot believe he actually did it. That is insane. No way. No way that just happened. I'm in shock right now.",
    whySelected: ["Strong emotional reaction hook", "High visual energy", "Self-contained moment", "Viral quote potential"],
    riskFlags: ["Contains loud sustained shouting"],
    similarity: 0.12,
    cropConfidence: 0.87,
    audioQuality: 0.92,
    visualQuality: 0.88,
    recommendedPlatform: "TikTok",
    suggestedCaption: "You won't believe what just happened...",
    suggestedHashtags: ["#kaicenat", "#streams", "#viral", "#reaction", "#shocked"],
    status: "new",
    thumbnail: "https://picsum.photos/seed/clip-c1/300/530",
  },
  {
    id: "c2",
    sourceId: "s1",
    profileId: "p1",
    score: 84,
    scoreBreakdown: {
      hook: 16,
      context: 13,
      emotion: 14,
      profileMatch: 14,
      quote: 8,
      visual: 8,
      topic: 4,
      length: 4,
      novelty: 3,
    },
    startTime: 1452.1,
    endTime: 1488.4,
    duration: 36.3,
    hook: "Argument escalates immediately when this is brought up.",
    title: "Argument about the sub rules gets heated",
    transcript: "Hold on, that's not what we agreed on. You said we were going to do it Friday. Now you're telling me Saturday? No, no, no. We had a deal. I'm not moving on this. The rules are clear, and you know it.",
    whySelected: ["Conflict-driven hook", "Clear narrative arc", "Strong takeaway line"],
    riskFlags: ["Heated argument", "Mild profanity detected"],
    similarity: 0.34,
    cropConfidence: 0.91,
    audioQuality: 0.89,
    visualQuality: 0.85,
    recommendedPlatform: "YouTube Shorts",
    suggestedCaption: "The argument that changed everything",
    suggestedHashtags: ["#kaicenat", "#argument", "#drama", "#streamer"],
    status: "new",
    thumbnail: "https://picsum.photos/seed/clip-c2/300/530",
  },
  {
    id: "c3",
    sourceId: "s1",
    profileId: "p1",
    score: 78,
    scoreBreakdown: {
      hook: 14,
      context: 12,
      emotion: 12,
      profileMatch: 13,
      quote: 8,
      visual: 7,
      topic: 4,
      length: 4,
      novelty: 4,
    },
    startTime: 4820.0,
    endTime: 4853.6,
    duration: 33.6,
    hook: "The surprise gift nobody saw coming.",
    title: "Fan sends the wildest package live on stream",
    transcript: "Wait what is this? Did someone just send me... no way. Is this actually real? Let me open it. Guys, I have no idea what's inside. Hold on. Oh my god. Oh my GOD. Are you kidding me?",
    whySelected: ["Surprise/reveal structure", "Genuine reaction", "Shareable moment"],
    riskFlags: [],
    similarity: 0.18,
    cropConfidence: 0.82,
    audioQuality: 0.9,
    visualQuality: 0.86,
    recommendedPlatform: "Instagram",
    suggestedCaption: "The best fan mail I've ever gotten",
    suggestedHashtags: ["#kaicenat", "#fanmail", "#surprise", "#reaction"],
    status: "reviewing",
    thumbnail: "https://picsum.photos/seed/clip-c3/300/530",
  },
  {
    id: "c4",
    sourceId: "s5",
    profileId: "p4",
    score: 93,
    scoreBreakdown: {
      hook: 19,
      context: 14,
      emotion: 15,
      profileMatch: 15,
      quote: 10,
      visual: 8,
      topic: 5,
      length: 4,
      novelty: 3,
    },
    startTime: 872.3,
    endTime: 897.1,
    duration: 24.8,
    hook: "\"You ever notice how weird airports are?\"",
    title: "Airport security bit brings house down",
    transcript: "You ever notice how weird airports are? Like, they make you take your shoes off. What, are you checking if my feet have a bomb? Sir, my feet smell, they don't explode. And then you put everything in a little plastic bin. I'm 35 years old, I should not be putting my belongings in a tray like a toddler at a daycare.",
    whySelected: ["Perfect setup/payoff structure", "Laugh track confirms audience response", "Relatable subject", "High shareability"],
    riskFlags: [],
    similarity: 0.08,
    cropConfidence: 0.94,
    audioQuality: 0.96,
    visualQuality: 0.91,
    recommendedPlatform: "TikTok",
    suggestedCaption: "Airport security makes no sense",
    suggestedHashtags: ["#comedy", "#standup", "#airport", "#relatable", "#funny"],
    status: "approved",
    thumbnail: "https://picsum.photos/seed/clip-c4/300/530",
  },
  {
    id: "c5",
    sourceId: "s5",
    profileId: "p4",
    score: 88,
    scoreBreakdown: {
      hook: 17,
      context: 14,
      emotion: 14,
      profileMatch: 14,
      quote: 9,
      visual: 7,
      topic: 5,
      length: 4,
      novelty: 4,
    },
    startTime: 1540.2,
    endTime: 1576.8,
    duration: 36.6,
    hook: "The story about his first date is absolutely brutal.",
    title: "The worst first date story you'll ever hear",
    transcript: "My first date was a disaster. I was 16, I had exactly 12 dollars, and I took her to a fast food place. Halfway through, she gets a text and says her mom is picking her up. Her mom. In a minivan. I just sat there with my chicken nuggets watching her leave.",
    whySelected: ["Storytelling arc", "Strong punchline", "Relatable embarrassment"],
    riskFlags: [],
    similarity: 0.22,
    cropConfidence: 0.9,
    audioQuality: 0.93,
    visualQuality: 0.88,
    recommendedPlatform: "Instagram",
    suggestedCaption: "We've all been there... right?",
    suggestedHashtags: ["#comedy", "#standup", "#firstdate", "#storytime"],
    status: "new",
    thumbnail: "https://picsum.photos/seed/clip-c5/300/530",
  },
  {
    id: "c6",
    sourceId: "s4",
    profileId: "p3",
    score: 79,
    scoreBreakdown: {
      hook: 14,
      context: 13,
      emotion: 10,
      profileMatch: 13,
      quote: 8,
      visual: 6,
      topic: 8,
      length: 4,
      novelty: 3,
    },
    startTime: 210.5,
    endTime: 268.0,
    duration: 57.5,
    hook: "\"AI regulation is going to change everything in 2025.\"",
    title: "The AI regulation debate nobody is talking about",
    transcript: "Here's the thing nobody is discussing. AI regulation is coming, and it's not going to look like what you think. The real debate isn't about models, it's about data. Who owns the training data? Who gets compensated? We're heading toward a reckoning that most people aren't prepared for.",
    whySelected: ["Topic-relevant", "Clear thesis statement", "Debate format", "High search relevance"],
    riskFlags: ["Complex topic - context completeness may vary"],
    similarity: 0.41,
    cropConfidence: 0.76,
    audioQuality: 0.94,
    visualQuality: 0.72,
    recommendedPlatform: "YouTube Shorts",
    suggestedCaption: "The AI regulation debate most people are missing",
    suggestedHashtags: ["#ai", "#tech", "#regulation", "#future", "#podcast"],
    status: "new",
    thumbnail: "https://picsum.photos/seed/clip-c6/300/530",
  },
  {
    id: "c7",
    sourceId: "s4",
    profileId: "p3",
    score: 71,
    scoreBreakdown: {
      hook: 12,
      context: 12,
      emotion: 8,
      profileMatch: 12,
      quote: 7,
      visual: 5,
      topic: 8,
      length: 4,
      novelty: 3,
    },
    startTime: 1800.0,
    endTime: 1845.3,
    duration: 45.3,
    hook: "Why the next phone you buy might be your last.",
    title: "Smartphone innovation is dead - here's why",
    transcript: "Let's be honest. Smartphone innovation has slowed down to a crawl. Every year we get a slightly better camera, a slightly faster chip, and a slightly bigger price tag. The question is: what happens when people stop upgrading every two years?",
    whySelected: ["Provocative thesis", "Search-relevant topic", "Clear point of view"],
    riskFlags: ["Potentially misleading framing"],
    similarity: 0.56,
    cropConfidence: 0.68,
    audioQuality: 0.91,
    visualQuality: 0.7,
    recommendedPlatform: "YouTube Shorts",
    suggestedCaption: "Are smartphones done improving?",
    suggestedHashtags: ["#smartphone", "#tech", "#innovation", "#phone"],
    status: "reviewing",
    thumbnail: "https://picsum.photos/seed/clip-c7/300/530",
  },
  {
    id: "c8",
    sourceId: "s10",
    profileId: "p5",
    score: 65,
    scoreBreakdown: {
      hook: 10,
      context: 10,
      emotion: 8,
      profileMatch: 10,
      quote: 6,
      visual: 8,
      topic: 5,
      length: 4,
      novelty: 4,
    },
    startTime: 45.0,
    endTime: 120.0,
    duration: 75.0,
    hook: "New product reveal at the 1 minute mark.",
    title: "Brand deal - product reveal cut",
    transcript: "Today we're taking a look at something I've been excited about for a while. This is the new product that's been all over my DMs. Let me unbox it and show you what it does.",
    whySelected: ["High production quality", "Sponsored content ready"],
    riskFlags: ["Sponsored content - disclosure required", "Brand mention heavy"],
    similarity: 0.0,
    cropConfidence: 0.95,
    audioQuality: 0.98,
    visualQuality: 0.96,
    recommendedPlatform: "Instagram",
    suggestedCaption: "This thing is actually incredible #ad",
    suggestedHashtags: ["#sponsored", "#product", "#review", "#newrelease"],
    status: "new",
    thumbnail: "https://picsum.photos/seed/clip-c8/300/530",
  },
];

// ========== RENDER JOBS ==========
export const renderJobs: RenderJob[] = [
  {
    id: "r1",
    clipId: "c4",
    profileId: "p4",
    clipTitle: "Airport security bit brings house down",
    priority: "high",
    status: "rendering",
    progress: 67,
    renderPreset: "Balanced 1080p",
    estimatedTime: "0:42 remaining",
    startedAt: "2024-03-15T13:12:00Z",
    retryCount: 0,
    device: "GPU - NVIDIA RTX 4090",
  },
  {
    id: "r2",
    clipId: "c1",
    profileId: "p1",
    clipTitle: "The most chaotic moment of the stream",
    priority: "urgent",
    status: "queued",
    progress: 0,
    renderPreset: "Maximum 1080p",
    estimatedTime: "~3 minutes",
    retryCount: 0,
    device: "GPU - NVIDIA RTX 4090",
  },
  {
    id: "r3",
    clipId: "c2",
    profileId: "p1",
    clipTitle: "Argument about the sub rules gets heated",
    priority: "normal",
    status: "queued",
    progress: 0,
    renderPreset: "Balanced 1080p",
    estimatedTime: "~2 minutes",
    retryCount: 0,
    device: "GPU - NVIDIA RTX 4090",
  },
  {
    id: "r4",
    clipId: "c3",
    profileId: "p1",
    clipTitle: "Fan sends the wildest package live on stream",
    priority: "normal",
    status: "queued",
    progress: 0,
    renderPreset: "Balanced 1080p",
    estimatedTime: "~2 minutes",
    retryCount: 0,
    device: "CPU",
  },
  {
    id: "r5",
    clipId: "c5",
    profileId: "p4",
    clipTitle: "The worst first date story you'll ever hear",
    priority: "low",
    status: "queued",
    progress: 0,
    renderPreset: "Fast 720p",
    estimatedTime: "~1 minute",
    retryCount: 0,
    device: "CPU",
  },
  {
    id: "r6",
    clipId: "c6",
    profileId: "p3",
    clipTitle: "The AI regulation debate nobody is talking about",
    priority: "high",
    status: "completed",
    progress: 100,
    renderPreset: "Balanced 1080p",
    estimatedTime: "Completed",
    startedAt: "2024-03-15T12:00:00Z",
    completedAt: "2024-03-15T12:02:34Z",
    retryCount: 0,
    outputSize: "47.2 MB",
    device: "GPU - NVIDIA RTX 4090",
  },
  {
    id: "r7",
    clipId: "c7",
    profileId: "p3",
    clipTitle: "Smartphone innovation is dead - here's why",
    priority: "normal",
    status: "failed",
    progress: 42,
    renderPreset: "Balanced 1080p",
    estimatedTime: "Failed",
    startedAt: "2024-03-15T11:30:00Z",
    errorMessage: "FONT_NOT_FOUND - Caption font 'Montserrat Bold' missing from system. Select another caption font.",
    retryCount: 2,
    device: "GPU - NVIDIA RTX 4090",
  },
];

// ========== SCHEDULED POSTS ==========
const today = new Date();
function addDays(days: number) {
  const d = new Date(today);
  d.setDate(d.getDate() + days);
  return d.toISOString().split("T")[0];
}

export const scheduledPosts: ScheduledPost[] = [
  { id: "sc1", clipId: "c4", clipTitle: "Airport security bit brings house down", profileId: "p4", platform: "TikTok", scheduledDate: addDays(0), scheduledTime: "10:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c4/150/265" },
  { id: "sc2", clipId: "c4", clipTitle: "Airport security bit brings house down", profileId: "p4", platform: "Instagram", scheduledDate: addDays(0), scheduledTime: "12:30", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c4/150/265" },
  { id: "sc3", clipId: "c5", clipTitle: "The worst first date story", profileId: "p4", platform: "TikTok", scheduledDate: addDays(0), scheduledTime: "15:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c5/150/265" },
  { id: "sc4", clipId: "c1", clipTitle: "The most chaotic moment", profileId: "p1", platform: "TikTok", scheduledDate: addDays(1), scheduledTime: "09:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c1/150/265" },
  { id: "sc5", clipId: "c6", clipTitle: "AI regulation debate", profileId: "p3", platform: "YouTube Shorts", scheduledDate: addDays(1), scheduledTime: "11:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c6/150/265" },
  { id: "sc6", clipId: "c2", clipTitle: "Argument about the sub rules", profileId: "p1", platform: "Instagram", scheduledDate: addDays(1), scheduledTime: "14:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c2/150/265" },
  { id: "sc7", clipId: "c3", clipTitle: "Fan sends the wildest package", profileId: "p1", platform: "TikTok", scheduledDate: addDays(2), scheduledTime: "10:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c3/150/265" },
  { id: "sc8", clipId: "c4", clipTitle: "Airport security bit", profileId: "p4", platform: "YouTube Shorts", scheduledDate: addDays(2), scheduledTime: "13:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c4/150/265" },
  { id: "sc9", clipId: "c5", clipTitle: "Worst first date story", profileId: "p4", platform: "Instagram", scheduledDate: addDays(3), scheduledTime: "16:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c5/150/265" },
  { id: "sc10", clipId: "c6", clipTitle: "AI regulation debate", profileId: "p3", platform: "Threads", scheduledDate: addDays(3), scheduledTime: "09:30", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c6/150/265" },
  { id: "sc11", clipId: "c7", clipTitle: "Smartphone innovation is dead", profileId: "p3", platform: "X", scheduledDate: addDays(4), scheduledTime: "12:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c7/150/265" },
  { id: "sc12", clipId: "c3", clipTitle: "Fan sends wildest package", profileId: "p1", platform: "YouTube Shorts", scheduledDate: addDays(5), scheduledTime: "14:00", status: "scheduled", thumbnail: "https://picsum.photos/seed/clip-c3/150/265" },
];

// ========== ANALYTICS ==========
export const analyticsData: AnalyticsPoint[] = Array.from({ length: 14 }, (_, i) => {
  const d = new Date(today);
  d.setDate(d.getDate() - 13 + i);
  const base = 12000 + Math.sin(i * 0.8) * 3000 + i * 400;
  return {
    date: d.toISOString().split("T")[0],
    views: Math.floor(base + Math.random() * 4000),
    likes: Math.floor(base * 0.07 + Math.random() * 300),
    comments: Math.floor(base * 0.012 + Math.random() * 80),
    shares: Math.floor(base * 0.02 + Math.random() * 100),
    clipsPosted: 2 + Math.floor(Math.random() * 3),
  };
});

export const hookTypeStats: HookTypeStat[] = [
  { type: "Strong Question", count: 47, avgViews: 42000, avgCompletion: 62 },
  { type: "Unexpected Statement", count: 38, avgViews: 58000, avgCompletion: 71 },
  { type: "Emotional Reaction", count: 56, avgViews: 65000, avgCompletion: 68 },
  { type: "Clear Disagreement", count: 29, avgViews: 47000, avgCompletion: 55 },
  { type: "Promise of Payoff", count: 34, avgViews: 38000, avgCompletion: 59 },
  { type: "Visual Action", count: 22, avgViews: 71000, avgCompletion: 74 },
  { type: "Recognizable Name", count: 18, avgViews: 52000, avgCompletion: 48 },
];

export const clipLengthStats: ClipLengthStat[] = [
  { length: "10-20s", count: 28, avgViews: 35000, avgCompletion: 82 },
  { length: "20-30s", count: 54, avgViews: 58000, avgCompletion: 71 },
  { length: "30-45s", count: 62, avgViews: 72000, avgCompletion: 58 },
  { length: "45-60s", count: 31, avgViews: 48000, avgCompletion: 42 },
  { length: "60-90s", count: 14, avgViews: 32000, avgCompletion: 31 },
];

// Dashboard totals
export const totals = {
  clipsPublished: 2665,
  clipsThisWeek: 42,
  totalViews: "142.7M",
  avgCompletionRate: "58%",
  sourcesProcessing: 5,
  candidatesReady: 32,
  renderJobs: 7,
  scheduledThisWeek: 28,
  storageUsed: "342 GB / 1 TB",
  gpuUtilization: 67,
  cpuUtilization: 41,
  errorCount: 1,
};
