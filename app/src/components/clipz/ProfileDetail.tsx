"use client";

import { useProfile, useProfilePlatforms, useProfileSources, useCandidateList, useSourceList } from "../../lib/api/hooks";
import { composeProfileView } from "../../lib/api/view-models";
import { Link } from "@tanstack/react-router";
import { ArrowLeft, Users, Globe, Video, Target, Zap, Shield, BarChart3 } from "lucide-react";

export function ProfileDetail({ profileId }: { profileId: string }) {
  const { data: profileData, isLoading, error } = useProfile(profileId);
  const { data: platformsData } = useProfilePlatforms(profileId);
  const { data: sourcesData } = useProfileSources(profileId);
  const { data: candidatesData } = useCandidateList({ profileId, pageSize: 10 });
  const { data: sourceListData } = useSourceList({ profileId, pageSize: 50 });

  if (isLoading) {
    return (
      <div className="p-4 lg:p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-64 bg-clipz-surface rounded" />
          <div className="h-48 bg-clipz-panel rounded-xl border border-clipz-border" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="h-40 bg-clipz-panel rounded-xl border border-clipz-border" />
            <div className="h-40 bg-clipz-panel rounded-xl border border-clipz-border" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !profileData) {
    return (
      <div className="p-4 lg:p-6">
        <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-8 text-center">
          <Shield size={40} className="mx-auto mb-3 text-rose-400" />
          <h3 className="text-[15px] font-semibold text-white mb-1">Profile Not Found</h3>
          <p className="text-[12px] text-clipz-text-muted mb-4">The profile you're looking for doesn't exist or was removed.</p>
          <Link to="/profiles" className="inline-flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white">
            <ArrowLeft size={14} /> Back to Profiles
          </Link>
        </div>
      </div>
    );
  }

  const view = composeProfileView(profileData, platformsData?.data, sourcesData?.data);
  const candidates = candidatesData?.data || [];
  const sourceVideos = sourceListData?.data || [];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex items-center gap-2">
        <Link to="/profiles" className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
          <ArrowLeft size={16} />
        </Link>
        <h2 className="text-lg font-semibold text-white">{view.name}</h2>
        <span className={`inline-block rounded-md border px-1.5 py-0.5 text-[10px] font-medium capitalize ${view.status === "active" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/20" : "bg-amber-500/15 text-amber-400 border-amber-500/20"}`}>
          {view.status}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-2 rounded-xl border border-clipz-border bg-clipz-panel p-5 space-y-4">
          <div className="flex items-center gap-4">
            <img src={view.image} alt="" className="h-16 w-16 rounded-xl border-2 border-clipz-panel bg-clipz-elevated object-cover" />
            <div>
              <h3 className="text-[16px] font-semibold text-white">{view.name}</h3>
              <p className="text-[11px] text-clipz-text-muted capitalize">{view.profileType} · {view.language}</p>
            </div>
          </div>
          <p className="text-[12px] text-clipz-text-muted leading-relaxed">{view.description}</p>
          <div className="flex flex-wrap gap-2">
            {view.contentThemes.map((t: string) => (
              <span key={t} className="rounded-md bg-clipz-surface border border-clipz-border px-2 py-0.5 text-[10px] text-clipz-text-muted">{t}</span>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-5 space-y-4">
          <h3 className="text-[13px] font-semibold text-white">Performance</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 rounded-lg bg-clipz-surface border border-clipz-border-soft">
              <p className="text-[20px] font-bold text-white">{view.clipsPublished}</p>
              <p className="text-[10px] text-clipz-text-dim">Published</p>
            </div>
            <div className="text-center p-3 rounded-lg bg-clipz-surface border border-clipz-border-soft">
              <p className="text-[20px] font-bold text-clipz-accent-soft">{view.clipsQueued}</p>
              <p className="text-[10px] text-clipz-text-dim">Queued</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-clipz-text-muted">Daily posting</span>
              <span className="text-white font-medium">{Object.values(view.postingSchedule).reduce((a: number, b: number) => a + b, 0)}/day</span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span className="text-clipz-text-muted">Auto-approval</span>
              <span className={view.autoApproval ? "text-emerald-400" : "text-amber-400"}>{view.autoApproval ? "Enabled" : "Disabled"}</span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span className="text-clipz-text-muted">Rights</span>
              <span className="text-white capitalize">{view.rightsStatus.replace("_", " ")}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-5">
          <h3 className="text-[13px] font-semibold text-white mb-3 flex items-center gap-2"><Globe size={14} className="text-clipz-accent-soft" /> Target Platforms</h3>
          {view.targetPlatforms.length > 0 ? (
            <div className="space-y-2">
              {view.targetPlatforms.map((p: string) => (
                <div key={p} className="flex items-center justify-between text-[12px]">
                  <span className="text-white">{p}</span>
                  <span className="text-clipz-text-dim">{view.postingSchedule[p] || 0}/day</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[11px] text-clipz-text-dim">No platforms configured</p>
          )}
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-5">
          <h3 className="text-[13px] font-semibold text-white mb-3 flex items-center gap-2"><Video size={14} className="text-clipz-accent-soft" /> Source Channels</h3>
          {view.sourceChannels.length > 0 ? (
            <div className="space-y-2">
              {view.sourceChannels.map((s: string) => (
                <div key={s} className="flex items-center gap-2 text-[12px]">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span className="text-white">{s}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[11px] text-clipz-text-dim">No source channels configured</p>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
          <h3 className="text-[13px] font-semibold text-white">Recent Candidates</h3>
          <Link to="/clip-lab" className="text-[11px] text-clipz-accent-soft hover:text-white">View all</Link>
        </div>
        {candidates.length > 0 ? (
          <div className="divide-y divide-clipz-border-soft">
            {candidates.slice(0, 5).map((c: any) => (
              <Link
                key={c.id}
                to="/clip-lab"
                className="flex items-center gap-3 px-4 py-3 hover:bg-clipz-surface/30 transition-colors"
              >
                <img src={c.thumbnailPath} alt="" className="h-10 w-16 rounded object-cover bg-clipz-elevated" />
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-white truncate font-medium">{c.title}</p>
                  <p className="text-[10px] text-clipz-text-dim">{Math.round(c.durationMs / 1000)}s · Score: {c.overallScore}</p>
                </div>
                <span className={`text-[10px] font-medium capitalize ${c.approvalStatus === "approved" ? "text-emerald-400" : c.approvalStatus === "rejected" ? "text-rose-400" : "text-amber-400"}`}>
                  {c.approvalStatus}
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <p className="text-[12px] text-clipz-text-dim">No candidates yet for this profile</p>
          </div>
        )}
      </div>

      <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
          <h3 className="text-[13px] font-semibold text-white">Sources</h3>
          <Link to="/sources" className="text-[11px] text-clipz-accent-soft hover:text-white">View all</Link>
        </div>
        {sourceVideos.length > 0 ? (
          <div className="divide-y divide-clipz-border-soft">
            {sourceVideos.slice(0, 5).map((s: any) => (
              <Link
                key={s.id}
                to="/sources"
                className="flex items-center gap-3 px-4 py-3 hover:bg-clipz-surface/30 transition-colors"
              >
                <img src={s.thumbnailPath} alt="" className="h-10 w-16 rounded object-cover bg-clipz-elevated" />
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-white truncate font-medium">{s.title}</p>
                  <p className="text-[10px] text-clipz-text-dim">{Math.round(s.durationMs / 1000 / 60)}m · {s.status}</p>
                </div>
                <span className={`text-[10px] font-medium capitalize ${s.status === "completed" || s.status === "candidates_ready" ? "text-emerald-400" : s.status === "failed" ? "text-rose-400" : "text-amber-400"}`}>
                  {s.status.replace("_", " ")}
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <p className="text-[12px] text-clipz-text-dim">No sources for this profile</p>
          </div>
        )}
      </div>
    </div>
  );
}