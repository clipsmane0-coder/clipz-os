"use client";

import { useState } from "react";
import { Plus, MoreHorizontal, Target, Video, Globe, Zap, Shield, Search } from "lucide-react";
import { profiles, Profile, ProfileType } from "../../lib/mock-data";

const typeLabels: Record<ProfileType, string> = {
  general: "General Channel",
  creator: "Creator Channel",
  topic: "Topic Channel",
  manual: "Manual Channel",
};

const typeColors: Record<ProfileType, string> = {
  general: "bg-violet-500/15 text-violet-400 border-violet-500/20",
  creator: "bg-cyan-500/15 text-cyan-400 border-cyan-500/20",
  topic: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  manual: "bg-amber-500/15 text-amber-400 border-amber-500/20",
};

function ProfileCard({ profile, onEdit }: { profile: Profile; onEdit: (p: Profile) => void }) {
  return (
    <div className="group relative overflow-hidden rounded-xl border border-clipz-border bg-clipz-panel transition-all hover:border-clipz-accent/40 hover:shadow-lg hover:shadow-violet-500/5">
      <div className="h-20 bg-gradient-to-br from-violet-600/20 via-transparent to-cyan-500/10 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-30" />
        <div className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2 py-0.5 border border-emerald-500/30">
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 pulse-dot" />
          <span className="text-[10px] font-medium text-emerald-400 capitalize">{profile.status}</span>
        </div>
      </div>

      <div className="px-4 pb-4 -mt-8">
        <div className="flex items-end justify-between mb-3">
          <img src={profile.image} alt="" className="h-16 w-16 rounded-xl border-2 border-clipz-panel bg-clipz-elevated object-cover shadow-lg" />
          <button className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface transition-colors opacity-0 group-hover:opacity-100">
            <MoreHorizontal size={16} />
          </button>
        </div>

        <h3 className="text-[14px] font-semibold text-white">{profile.name}</h3>
        <span className={`inline-block mt-1 rounded-md border px-1.5 py-0.5 text-[10px] font-medium ${typeColors[profile.type]}`}>
          {typeLabels[profile.type]}
        </span>

        <p className="mt-2.5 text-[11px] text-clipz-text-muted line-clamp-2 leading-relaxed">{profile.description}</p>

        <div className="mt-3 grid grid-cols-3 gap-2 py-3 border-t border-clipz-border-soft">
          <div>
            <p className="text-[14px] font-bold text-white">{profile.clipsPublished}</p>
            <p className="text-[9px] text-clipz-text-dim uppercase tracking-wider">Published</p>
          </div>
          <div>
            <p className="text-[14px] font-bold text-clipz-accent-soft">{profile.clipsQueued}</p>
            <p className="text-[9px] text-clipz-text-dim uppercase tracking-wider">Queued</p>
          </div>
          <div>
            <p className="text-[14px] font-bold text-cyan-400">
              {Object.values(profile.postingSchedule).reduce((a, b) => a + b, 0)}/day
            </p>
            <p className="text-[9px] text-clipz-text-dim uppercase tracking-wider">Posts</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 mb-3">
          <span className="text-[10px] text-clipz-text-dim">Targets:</span>
          {profile.targetPlatforms.slice(0, 3).map((p) => (
            <span key={p} className="rounded-md bg-clipz-surface px-1.5 py-0.5 text-[9px] text-clipz-text-muted border border-clipz-border-soft">
              {p}
            </span>
          ))}
          {profile.targetPlatforms.length > 3 && (
            <span className="text-[9px] text-clipz-text-dim">+{profile.targetPlatforms.length - 3}</span>
          )}
        </div>

        <div className="flex gap-2">
          <button onClick={() => onEdit(profile)} className="flex-1 rounded-md bg-clipz-surface border border-clipz-border px-2 py-1.5 text-[11px] font-medium text-white hover:bg-clipz-elevated transition-colors">
            Edit Profile
          </button>
          <button className="rounded-md bg-clipz-accent px-2 py-1.5 text-[11px] font-medium text-white hover:bg-clipz-accent/90 transition-colors">
            View
          </button>
        </div>
      </div>
    </div>
  );
}

export function ProfilesPage() {
  const [filter, setFilter] = useState<ProfileType | "all">("all");
  const [search, setSearch] = useState("");
  const [editingProfile, setEditingProfile] = useState<Profile | null>(null);

  const filtered = profiles.filter((p) => {
    if (filter !== "all" && p.type !== filter) return false;
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Creator Profiles</h2>
          <p className="text-[12px] text-clipz-text-muted">Manage clip profiles, sources, targets, and preferences</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90 transition-colors glow-accent">
          <Plus size={14} />
          New Profile
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {(["all", "creator", "general", "topic", "manual"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`shrink-0 rounded-lg px-3 py-1.5 text-[12px] font-medium transition-all ${
                filter === t ? "bg-clipz-accent text-white" : "bg-clipz-surface border border-clipz-border text-clipz-text-muted hover:text-white"
              }`}
            >
              {t === "all" ? "All Profiles" : typeLabels[t as ProfileType]}
            </button>
          ))}
        </div>
        <div className="sm:ml-auto relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-clipz-text-dim" />
          <input
            type="text"
            placeholder="Search profiles..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full sm:w-64 h-8 rounded-lg border border-clipz-border bg-clipz-surface pl-8 pr-3 text-[12px] text-clipz-text placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <button className="group flex flex-col items-center justify-center rounded-xl border border-dashed border-clipz-border bg-clipz-panel/50 p-6 text-clipz-text-muted hover:border-clipz-accent/40 hover:text-clipz-accent-soft hover:bg-clipz-accent/5 transition-all min-h-[280px]">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-clipz-surface border border-clipz-border group-hover:border-clipz-accent/30 group-hover:bg-clipz-accent/10 transition-all mb-3">
            <Plus size={20} />
          </div>
          <p className="text-[13px] font-medium">Create Profile</p>
          <p className="text-[11px] text-clipz-text-dim mt-1">Start with a template</p>
        </button>

        {filtered.map((profile) => (
          <ProfileCard key={profile.id} profile={profile} onEdit={setEditingProfile} />
        ))}
      </div>

      {editingProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-2xl max-h-[90dvh] overflow-y-auto rounded-xl border border-clipz-border bg-clipz-panel shadow-2xl">
            <div className="sticky top-0 flex items-center justify-between border-b border-clipz-border-soft bg-clipz-panel p-4 z-10">
              <div>
                <h3 className="text-[14px] font-semibold text-white">Edit Profile</h3>
                <p className="text-[11px] text-clipz-text-muted">{editingProfile.name}</p>
              </div>
              <button onClick={() => setEditingProfile(null)} className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 space-y-5">
              <div>
                <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
                  <Target size={14} className="text-clipz-accent-soft" /> Basic Information
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">Profile Name</label>
                    <input type="text" defaultValue={editingProfile.name} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50" />
                  </div>
                  <div>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">Profile Type</label>
                    <select defaultValue={editingProfile.type} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50">
                      <option value="creator">Creator Channel</option>
                      <option value="general">General Channel</option>
                      <option value="topic">Topic Channel</option>
                      <option value="manual">Manual Channel</option>
                    </select>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
                  <Video size={14} className="text-cyan-400" /> Source Channels
                </h4>
                <div className="flex flex-wrap gap-2">
                  {editingProfile.sourceChannels.map((s) => (
                    <span key={s} className="inline-flex items-center gap-1.5 rounded-md bg-clipz-surface border border-clipz-border px-2 py-1 text-[11px] text-white">
                      {s}
                      <button className="text-clipz-text-dim hover:text-rose-400">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M18 6L6 18M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ))}
                  <button className="rounded-md border border-dashed border-clipz-border px-2 py-1 text-[11px] text-clipz-text-dim hover:text-white hover:border-clipz-accent/40">
                    + Add source
                  </button>
                </div>
              </div>
              <div>
                <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
                  <Globe size={14} className="text-emerald-400" /> Target Platforms
                </h4>
                <div className="flex flex-wrap gap-2">
                  {["TikTok", "Instagram", "YouTube Shorts", "Threads", "X", "Facebook"].map((p) => {
                    const active = editingProfile.targetPlatforms.includes(p);
                    return (
                      <button
                        key={p}
                        className={`rounded-md border px-2.5 py-1 text-[11px] font-medium transition-colors ${
                          active ? "bg-clipz-accent/15 text-clipz-accent-soft border-clipz-accent/30" : "bg-clipz-surface text-clipz-text-muted border-clipz-border hover:text-white"
                        }`}
                      >
                        {p}
                      </button>
                    );
                  })}
                </div>
              </div>
              <div>
                <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
                  <Zap size={14} className="text-amber-400" /> Clip Preferences
                </h4>
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">Min Length (s)</label>
                    <input type="number" defaultValue={editingProfile.clipLengths.min} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50" />
                  </div>
                  <div>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">Max Length (s)</label>
                    <input type="number" defaultValue={editingProfile.clipLengths.max} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50" />
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {editingProfile.contentThemes.map((t) => (
                    <span key={t} className="rounded-md bg-clipz-surface border border-clipz-border px-1.5 py-0.5 text-[10px] text-clipz-text-muted">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
                  <Shield size={14} className="text-rose-400" /> Rights &amp; Safety
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">Rights Status</label>
                    <select defaultValue={editingProfile.rightsStatus} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50">
                      <option value="owned">Owned</option>
                      <option value="licensed">Licensed</option>
                      <option value="creator-approved">Creator Approved</option>
                      <option value="transformative-review">Transformative Review</option>
                      <option value="unknown">Unknown</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">Safety Level</label>
                    <select defaultValue={editingProfile.safetyLevel} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50">
                      <option value="low">Low</option>
                      <option value="moderate">Moderate</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div className="sticky bottom-0 flex items-center justify-end gap-2 border-t border-clipz-border-soft bg-clipz-panel p-4">
              <button onClick={() => setEditingProfile(null)} className="rounded-md border border-clipz-border px-3 py-1.5 text-[12px] text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
                Cancel
              </button>
              <button className="rounded-md bg-clipz-accent px-3 py-1.5 text-[12px] font-medium text-white hover:bg-clipz-accent/90">
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
