// ============================================================
// CLIPZ — API Client (mode-switching layer)
// ============================================================
// Separates mock and real API modes explicitly.
// Unsupported features in real mode throw a clear error
// instead of silently falling back to mock data.
// ============================================================

import { apiConfig } from "./config";
import * as mock from "./mock-client";
import * as real from "./real-client";

function unsupported(name: string): () => never {
  return () => { throw new Error(`Not available in real API mode yet: ${name}`); };
}

// Select implementation based on mode
const impl = (apiConfig.isReal ? real : mock) as any;
const unsupportedFn = unsupported;

// === HEALTH ===
export const getHealth = impl.getHealth;

// === DASHBOARD ===
export const getDashboardOverview = impl.getDashboardOverview;

// === PROFILES ===
export const listProfiles = impl.listProfiles;
export const getProfile = impl.getProfile;
export const createProfile = impl.createProfile;
export const updateProfile = impl.updateProfile;
export const deleteProfile = impl.deleteProfile;
export const pauseProfile = impl.pauseProfile;
export const resumeProfile = impl.resumeProfile;
export const archiveProfile = impl.archiveProfile;
export const getProfilePlatforms = apiConfig.isReal ? unsupportedFn("getProfilePlatforms") : mock.getProfilePlatforms;
export const getProfileSources = apiConfig.isReal ? unsupportedFn("getProfileSources") : mock.getProfileSources;

// === SOURCES ===
export const listSources = impl.listSources;
export const getSource = impl.getSource;
export const createSource = impl.createSource;
export const updateSource = impl.updateSource;
export const deleteSource = impl.deleteSource;
export const archiveSource = impl.archiveSource;
export const getSourceTranscript = apiConfig.isReal ? unsupportedFn("getSourceTranscript") : mock.getSourceTranscript;
export const getTranscriptSegments = apiConfig.isReal ? unsupportedFn("getTranscriptSegments") : mock.getTranscriptSegments;
export const getSourceScenes = apiConfig.isReal ? unsupportedFn("getSourceScenes") : mock.getSourceScenes;

// === CANDIDATES ===
export const listCandidates = impl.listCandidates;
export const getCandidate = impl.getCandidate;
export const createCandidate = impl.createCandidate;
export const updateCandidate = impl.updateCandidate;
export const approveCandidate = impl.approveCandidate;
export const rejectCandidate = impl.rejectCandidate;
export const archiveCandidate = impl.archiveCandidate;
export const getCandidateScores = apiConfig.isReal ? unsupportedFn("getCandidateScores") : mock.getCandidateScores;
export const getCandidateEdits = apiConfig.isReal ? unsupportedFn("getCandidateEdits") : mock.getCandidateEdits;

// === JOBS ===
export const listJobs = impl.listJobs;
export const getJob = impl.getJob;
export const createJob = impl.createJob;
export const retryJob = impl.retryJob;
export const cancelJob = impl.cancelJob;
export const pauseJob = impl.pauseJob;
export const resumeJob = impl.resumeJob;

// === RENDERS ===
export const listRenders = impl.listRenders;

// === SCHEDULES ===
export const listSchedules = impl.listSchedules;
export const getSchedule = impl.getSchedule;
export const createSchedule = impl.createSchedule;

// === ANALYTICS ===
export const getAnalyticsOverview = impl.getAnalyticsOverview;
export const getAnalyticsTimeseries = impl.getAnalyticsTimeseries;
export const getHookTypeStats = impl.getHookTypeStats;
export const getClipLengthStats = impl.getClipLengthStats;
export const getProfilePerformance = impl.getProfilePerformance;

// === PRESETS (unsupported in real mode) ===
export const getBrandingPresets = apiConfig.isReal ? unsupportedFn("getBrandingPresets") : mock.getBrandingPresets;
export const getCaptionPresets = apiConfig.isReal ? unsupportedFn("getCaptionPresets") : mock.getCaptionPresets;
export const getRenderPresets = apiConfig.isReal ? unsupportedFn("getRenderPresets") : mock.getRenderPresets;
export const getScoringPresets = apiConfig.isReal ? unsupportedFn("getScoringPresets") : mock.getScoringPresets;

// === NOTIFICATIONS ===
export const listNotifications = impl.listNotifications;
export const markNotificationRead = impl.markNotificationRead;

// === SETTINGS ===
export const getSystemSettings = impl.getSystemSettings;
export const updateSystemSetting = impl.updateSystemSetting;
export const getProfileSettings = impl.getProfileSettings;
export const updateProfileSetting = impl.updateProfileSetting;

// === SOURCE UPLOAD ===
export const uploadSource = impl.uploadSource;
export const registerSourceUrl = impl.registerSourceUrl;