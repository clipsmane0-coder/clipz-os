// ============================================================
// CLIPZ — React Query Hooks
// ============================================================
// Frontend components should import data from here, never from
// raw mock data. These hooks use TanStack Query for caching,
// refetching, and state management, with the mock API client
// simulating real network requests.
//
// All data is returned in camelCase via the mapper.
// ============================================================

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from "@tanstack/react-query";
import * as api from "./client";
import { snakeToCamel, camelToSnake } from "./mapper";
import type {
  FProfile,
  FSource,
  FCandidate,
  FCandidateScore,
  FJob,
  FSchedule,
  FNotification,
  FRenderOutput,
  FDashboardOverview,
  FProfilePerformance,
  FAnalyticsSnapshot,
  FBrandingPreset,
  FCaptionPreset,
  FRenderPreset,
  FScoringPreset,
  FTranscript,
  FTranscriptSegment,
  FScene,
  FProfilePlatform,
  FProfileSource,
  HookTypeStat,
  ClipLengthStat,
  AnalyticsPoint,
  FProfileView,
  FSourceView,
  FCandidateView,
  FJobView,
  FScheduleView,
  FLibraryItem,
} from "./mapper";
import {
  composeProfileView,
  composeSourceView,
  composeCandidateView,
  composeJobView,
  composeScheduleView,
  composeLibraryItem,
} from "./view-models";

// ---- Query keys ----
export const queryKeys = {
  all: ["clipz"] as const,
  dashboard: () => [...queryKeys.all, "dashboard"] as const,
  profiles: (params?: any) => [...queryKeys.all, "profiles", params] as const,
  profile: (id: string) => [...queryKeys.all, "profile", id] as const,
  profilePlatforms: (id: string) => [...queryKeys.all, "profile", id, "platforms"] as const,
  profileSources: (id: string) => [...queryKeys.all, "profile", id, "sources"] as const,
  sources: (params?: any) => [...queryKeys.all, "sources", params] as const,
  source: (id: string) => [...queryKeys.all, "source", id] as const,
  sourceTranscript: (id: string) => [...queryKeys.all, "source", id, "transcript"] as const,
  transcriptSegments: (id: string) => [...queryKeys.all, "transcript", id, "segments"] as const,
  sourceScenes: (id: string) => [...queryKeys.all, "source", id, "scenes"] as const,
  candidates: (params?: any) => [...queryKeys.all, "candidates", params] as const,
  candidate: (id: string) => [...queryKeys.all, "candidate", id] as const,
  candidateScores: (id: string) => [...queryKeys.all, "candidate", id, "scores"] as const,
  candidateEdits: (id: string) => [...queryKeys.all, "candidate", id, "edits"] as const,
  jobs: (params?: any) => [...queryKeys.all, "jobs", params] as const,
  job: (id: string) => [...queryKeys.all, "job", id] as const,
  renders: (params?: any) => [...queryKeys.all, "renders", params] as const,
  schedules: (params?: any) => [...queryKeys.all, "schedules", params] as const,
  schedule: (id: string) => [...queryKeys.all, "schedule", id] as const,
  analyticsOverview: (params?: any) => [...queryKeys.all, "analytics", "overview", params] as const,
  analyticsTimeseries: (params?: any) => [...queryKeys.all, "analytics", "timeseries", params] as const,
  analyticsHookTypes: () => [...queryKeys.all, "analytics", "hook-types"] as const,
  analyticsClipLengths: () => [...queryKeys.all, "analytics", "clip-lengths"] as const,
  analyticsProfiles: () => [...queryKeys.all, "analytics", "profiles"] as const,
  notifications: (params?: any) => [...queryKeys.all, "notifications", params] as const,
  brandingPresets: (profileId?: string) => [...queryKeys.all, "presets", "branding", profileId] as const,
  captionPresets: (profileId?: string) => [...queryKeys.all, "presets", "caption", profileId] as const,
  renderPresets: (profileId?: string) => [...queryKeys.all, "presets", "render", profileId] as const,
  scoringPresets: (profileId?: string) => [...queryKeys.all, "presets", "scoring", profileId] as const,
  systemSettings: () => [...queryKeys.all, "settings"] as const,
  health: () => [...queryKeys.all, "health"] as const,
};

// ============================================================
// DASHBOARD
// ============================================================

export function useDashboardOverview(): UseQueryResult<FDashboardOverview> {
  return useQuery({
    queryKey: queryKeys.dashboard(),
    queryFn: async () => {
      const resp = await api.getDashboardOverview();
      return snakeToCamel(resp.data);
    },
  });
}

// ============================================================
// PROFILES
// ============================================================

export interface UseProfilesParams {
  page?: number;
  pageSize?: number;
  status?: string;
  type?: string;
}

export function useProfiles(params: UseProfilesParams = {}): UseQueryResult<{
  data: FProfile[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.profiles(params),
    queryFn: async () => {
      const resp = await api.listProfiles({
        page: params.page,
        page_size: params.pageSize,
        status: params.status,
        type: params.type,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

export function useProfile(id: string): UseQueryResult<FProfile> {
  return useQuery({
    queryKey: queryKeys.profile(id),
    queryFn: async () => {
      const resp = await api.getProfile(id);
      return snakeToCamel(resp.data);
    },
    enabled: !!id,
  });
}

export function useProfilePlatforms(profileId: string): UseQueryResult<FProfilePlatform[]> {
  return useQuery({
    queryKey: queryKeys.profilePlatforms(profileId),
    queryFn: async () => {
      const resp = await api.getProfilePlatforms(profileId);
      return snakeToCamel<any[]>(resp.data);
    },
    enabled: !!profileId,
  });
}

export function useProfileSources(profileId: string): UseQueryResult<FProfileSource[]> {
  return useQuery({
    queryKey: queryKeys.profileSources(profileId),
    queryFn: async () => {
      const resp = await api.getProfileSources(profileId);
      return snakeToCamel<any[]>(resp.data);
    },
    enabled: !!profileId,
  });
}

// ============================================================
// SOURCES
// ============================================================

export interface UseSourcesParams {
  page?: number;
  pageSize?: number;
  status?: string;
  profileId?: string;
}

export function useSources(params: UseSourcesParams = {}): UseQueryResult<{
  data: FSource[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.sources(params),
    queryFn: async () => {
      const resp = await api.listSources({
        page: params.page,
        page_size: params.pageSize,
        status: params.status,
        profile_id: params.profileId,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

export function useSource(id: string): UseQueryResult<FSource> {
  return useQuery({
    queryKey: queryKeys.source(id),
    queryFn: async () => {
      const resp = await api.getSource(id);
      return snakeToCamel(resp.data);
    },
    enabled: !!id,
  });
}

export function useSourceTranscript(sourceId: string): UseQueryResult<FTranscript> {
  return useQuery({
    queryKey: queryKeys.sourceTranscript(sourceId),
    queryFn: async () => {
      const resp = await api.getSourceTranscript(sourceId);
      return snakeToCamel(resp.data);
    },
    enabled: !!sourceId,
  });
}

export function useTranscriptSegments(transcriptId: string): UseQueryResult<FTranscriptSegment[]> {
  return useQuery({
    queryKey: queryKeys.transcriptSegments(transcriptId),
    queryFn: async () => {
      const resp = await api.getTranscriptSegments(transcriptId);
      return snakeToCamel<any[]>(resp.data);
    },
    enabled: !!transcriptId,
  });
}

export function useSourceScenes(sourceId: string): UseQueryResult<FScene[]> {
  return useQuery({
    queryKey: queryKeys.sourceScenes(sourceId),
    queryFn: async () => {
      const resp = await api.getSourceScenes(sourceId);
      return snakeToCamel<any[]>(resp.data);
    },
    enabled: !!sourceId,
  });
}

// ============================================================
// CANDIDATES
// ============================================================

export interface UseCandidatesParams {
  page?: number;
  pageSize?: number;
  approvalStatus?: string;
  profileId?: string;
  sourceId?: string;
  minScore?: number;
}

export function useCandidates(params: UseCandidatesParams = {}): UseQueryResult<{
  data: FCandidate[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.candidates(params),
    queryFn: async () => {
      const resp = await api.listCandidates({
        page: params.page,
        page_size: params.pageSize,
        approval_status: params.approvalStatus,
        profile_id: params.profileId,
        source_id: params.sourceId,
        min_score: params.minScore,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

export function useCandidate(id: string): UseQueryResult<FCandidate> {
  return useQuery({
    queryKey: queryKeys.candidate(id),
    queryFn: async () => {
      const resp = await api.getCandidate(id);
      return snakeToCamel(resp.data);
    },
    enabled: !!id,
  });
}

export function useCandidateScores(candidateId: string): UseQueryResult<FCandidateScore[]> {
  return useQuery({
    queryKey: queryKeys.candidateScores(candidateId),
    queryFn: async () => {
      const resp = await api.getCandidateScores(candidateId);
      return snakeToCamel<any[]>(resp.data);
    },
    enabled: !!candidateId,
  });
}

// ============================================================
// JOBS
// ============================================================

export interface UseJobsParams {
  page?: number;
  pageSize?: number;
  status?: string;
  jobType?: string;
  profileId?: string;
}

export function useJobs(params: UseJobsParams = {}): UseQueryResult<{
  data: FJob[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.jobs(params),
    queryFn: async () => {
      const resp = await api.listJobs({
        page: params.page,
        page_size: params.pageSize,
        status: params.status,
        job_type: params.jobType,
        profile_id: params.profileId,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

export function useJob(id: string): UseQueryResult<FJob> {
  return useQuery({
    queryKey: queryKeys.job(id),
    queryFn: async () => {
      const resp = await api.getJob(id);
      return snakeToCamel(resp.data);
    },
    enabled: !!id,
  });
}

// ============================================================
// RENDERS
// ============================================================

export function useRenders(params: { page?: number; pageSize?: number; status?: string } = {}): UseQueryResult<{
  data: FRenderOutput[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.renders(params),
    queryFn: async () => {
      const resp = await api.listRenders({
        page: params.page,
        page_size: params.pageSize,
        status: params.status,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

// ============================================================
// SCHEDULES
// ============================================================

export interface UseSchedulesParams {
  page?: number;
  pageSize?: number;
  status?: string;
  platform?: string;
  profileId?: string;
  dateFrom?: string;
  dateTo?: string;
}

export function useSchedules(params: UseSchedulesParams = {}): UseQueryResult<{
  data: FSchedule[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.schedules(params),
    queryFn: async () => {
      const resp = await api.listSchedules({
        page: params.page,
        page_size: params.pageSize,
        status: params.status,
        platform: params.platform,
        profile_id: params.profileId,
        date_from: params.dateFrom,
        date_to: params.dateTo,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

// ============================================================
// ANALYTICS
// ============================================================

export function useAnalyticsOverview(params: { range?: string; profileId?: string } = {}): UseQueryResult<any> {
  return useQuery({
    queryKey: queryKeys.analyticsOverview(params),
    queryFn: async () => {
      const resp = await api.getAnalyticsOverview({
        range: params.range,
        profile_id: params.profileId,
      });
      return snakeToCamel(resp.data);
    },
  });
}

export function useAnalyticsTimeseries(params: { range?: string; profileId?: string } = {}): UseQueryResult<AnalyticsPoint[]> {
  return useQuery({
    queryKey: queryKeys.analyticsTimeseries(params),
    queryFn: async () => {
      const resp = await api.getAnalyticsTimeseries({
        range: params.range,
        profile_id: params.profileId,
      });
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

export function useHookTypeStats(): UseQueryResult<HookTypeStat[]> {
  return useQuery({
    queryKey: queryKeys.analyticsHookTypes(),
    queryFn: async () => {
      const resp = await api.getHookTypeStats();
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

export function useClipLengthStats(): UseQueryResult<ClipLengthStat[]> {
  return useQuery({
    queryKey: queryKeys.analyticsClipLengths(),
    queryFn: async () => {
      const resp = await api.getClipLengthStats();
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

export function useProfilePerformance(): UseQueryResult<FProfilePerformance[]> {
  return useQuery({
    queryKey: queryKeys.analyticsProfiles(),
    queryFn: async () => {
      const resp = await api.getProfilePerformance();
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

// ============================================================
// NOTIFICATIONS
// ============================================================

export function useNotifications(params: { page?: number; pageSize?: number; unreadOnly?: boolean } = {}): UseQueryResult<{
  data: FNotification[];
  total: number;
  page: number;
  pageSize: number;
}> {
  return useQuery({
    queryKey: queryKeys.notifications(params),
    queryFn: async () => {
      const resp = await api.listNotifications({
        page: params.page,
        page_size: params.pageSize,
        unread_only: params.unreadOnly,
      });
      return {
        data: snakeToCamel<any[]>(resp.data),
        total: resp.meta.total,
        page: resp.meta.page,
        pageSize: resp.meta.page_size,
      };
    },
  });
}

// ============================================================
// PRESETS
// ============================================================

export function useBrandingPresets(profileId?: string): UseQueryResult<FBrandingPreset[]> {
  return useQuery({
    queryKey: queryKeys.brandingPresets(profileId),
    queryFn: async () => {
      const resp = await api.getBrandingPresets(profileId);
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

export function useCaptionPresets(profileId?: string): UseQueryResult<FCaptionPreset[]> {
  return useQuery({
    queryKey: queryKeys.captionPresets(profileId),
    queryFn: async () => {
      const resp = await api.getCaptionPresets(profileId);
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

export function useRenderPresets(profileId?: string): UseQueryResult<FRenderPreset[]> {
  return useQuery({
    queryKey: queryKeys.renderPresets(profileId),
    queryFn: async () => {
      const resp = await api.getRenderPresets(profileId);
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

export function useScoringPresets(profileId?: string): UseQueryResult<FScoringPreset[]> {
  return useQuery({
    queryKey: queryKeys.scoringPresets(profileId),
    queryFn: async () => {
      const resp = await api.getScoringPresets(profileId);
      return snakeToCamel<any[]>(resp.data);
    },
  });
}

// ============================================================
// HEALTH
// ============================================================

export function useHealth(): UseQueryResult<{
  api: boolean;
  database: boolean;
  worker: boolean;
  ffmpeg: boolean;
  transcription: boolean;
  storage: boolean;
  version: string;
}> {
  return useQuery({
    queryKey: queryKeys.health(),
    queryFn: async () => {
      const resp = await api.getHealth();
      return snakeToCamel(resp.data);
    },
    refetchInterval: 30000,
  });
}

// ============================================================
// SETTINGS
// ============================================================

export function useSystemSettings(): UseQueryResult<any> {
  return useQuery({
    queryKey: queryKeys.systemSettings(),
    queryFn: async () => {
      const resp = await api.getSystemSettings();
      return snakeToCamel(resp.data);
    },
  });
}

// ============================================================
// VIEW MODEL HOOKS (composed for UI display)
// ============================================================
// These hooks wrap the base data hooks and compose view models.
// They use `as any` because spreading a TanStack Query result
// (a discriminated union) produces an object that TypeScript
// can't statically verify as a valid union variant. At runtime
// the data shape is correct.

// --- Profiles ---
export function useProfileList(params: UseProfilesParams = {}): UseQueryResult<{ data: FProfileView[]; total: number; page: number; pageSize: number }> {
  const q = useProfiles(params);
  return {
    ...q,
    data: q.data ? { ...q.data, data: q.data.data.map((p: any) => composeProfileView(p, [], [])) } : undefined,
  } as any;
}

// --- Sources ---
export function useSourceList(params: UseSourcesParams = {}): UseQueryResult<{ data: FSourceView[]; total: number; page: number; pageSize: number }> {
  const q = useSources(params);
  const profilesQ = useProfiles({ pageSize: 100 });
  return {
    ...q,
    data: q.data && profilesQ.data
      ? { ...q.data, data: q.data.data.map((s: any) => composeSourceView(s, (profilesQ.data.data as any[]).find((p: any) => p.id === s.profileId)?.name || "")) }
      : undefined,
  } as any;
}

// --- Candidates ---
export function useCandidateList(params: UseCandidatesParams = {}): UseQueryResult<{ data: FCandidateView[]; total: number; page: number; pageSize: number }> {
  const q = useCandidates(params);
  return {
    ...q,
    data: q.data ? { ...q.data, data: q.data.data.map((c: any) => composeCandidateView(c, c.scoreBreakdown || [])) } : undefined,
  } as any;
}

// --- Jobs (render queue) ---
export function useJobList(params: UseJobsParams = {}): UseQueryResult<{ data: FJobView[]; total: number; page: number; pageSize: number }> {
  const q = useJobs(params);
  return {
    ...q,
    data: q.data ? { ...q.data, data: q.data.data.map((j: any) => composeJobView(j)) } : undefined,
  } as any;
}

// --- Schedules (calendar) ---
export function useScheduleList(params: UseSchedulesParams = {}): UseQueryResult<{ data: FScheduleView[]; total: number; page: number; pageSize: number }> {
  const q = useSchedules(params);
  return {
    ...q,
    data: q.data ? { ...q.data, data: q.data.data.map((s: any) => composeScheduleView(s)) } : undefined,
  } as any;
}

// --- Library (published + scheduled candidates with stats) ---
export function useLibrary(params: UseCandidatesParams = {}): UseQueryResult<{ data: FLibraryItem[]; total: number; page: number; pageSize: number }> {
  const q = useCandidates(params);
  return {
    ...q,
    data: q.data
      ? {
          ...q.data,
          data: q.data.data.flatMap((c: any, i: number) => {
            const items: FLibraryItem[] = [];
            items.push(composeLibraryItem(c, c.scoreBreakdown || [], { views: i * 12500 + Math.floor(Math.random() * 50000), likes: Math.floor((i * 12500 + 10000) * 0.07), comments: Math.floor((i * 12500 + 10000) * 0.012), platform: (["tiktok", "instagram", "youtube", "threads"] as const)[i % 4], publishedAt: i % 2 === 0 ? new Date(Date.now() - i * 86400000).toISOString() : undefined }));
            if (i < 6) items.push(composeLibraryItem({ ...c, id: `${c.id}-b`, thumbnailPath: c.thumbnailPath }, c.scoreBreakdown || [], { views: 80000 + i * 35000, likes: Math.floor((80000 + i * 35000) * 0.08), comments: Math.floor((80000 + i * 35000) * 0.015), platform: (["tiktok", "instagram", "youtube", "threads"] as const)[(i + 1) % 4], publishedAt: new Date(Date.now() - (i + 3) * 86400000).toISOString() }));
            return items;
          }),
        }
      : undefined,
  } as any;
}
