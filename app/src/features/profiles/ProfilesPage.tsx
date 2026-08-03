"use client";

import { useState } from "react";
import { Plus, MoreHorizontal, Target, Video, Globe, Zap, Shield, Search, X, Check, Loader2, Users } from "lucide-react";
import { useProfileList } from "../../lib/api/hooks";
import { useCreateProfile, useUpdateProfile, useDeleteProfile } from "../../lib/api/hooks";
import type { ProfileType } from "../../lib/types/clipz";
import type { FProfileView } from "../../lib/api/mapper";

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

const allPlatforms = ["TikTok", "Instagram", "YouTube Shorts", "Threads", "X", "Facebook"];

const defaultForm = {
  name: "",
  type: "creator" as ProfileType,
  description: "",
  image: "https://api.dicebear.com/7.x/glass/svg?seed=clipz",
  targetPlatforms: [] as string[],
  clipLengths: { min: 15, max: 60 },
  contentThemes: [] as string[],
  rightsStatus: "owned",
  safetyLevel: "moderate",
  autoApproval: false,
  sourceChannels: [] as string[],
  postingSchedule: {} as Record<string, number>,
};

function ProfileCard({ profile, onEdit, onDelete }: { profile: FProfileView; onEdit: (p: FProfileView) => void; onDelete: (id: string) => void }) {
  const [menuOpen, setMenuOpen] = useState(false);
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
          <div className="relative">
            <button onClick={() => setMenuOpen(!menuOpen)} className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface transition-colors opacity-0 group-hover:opacity-100">
              <MoreHorizontal size={16} />
            </button>
            {menuOpen && (
              <div className="absolute right-0 top-full mt-1 w-32 rounded-lg border border-clipz-border bg-clipz-panel shadow-xl z-20 py-1">
                <button onClick={() => { setMenuOpen(false); onEdit(profile); }} className="w-full px-3 py-1.5 text-[11px] text-left text-clipz-text-muted hover:text-white hover:bg-clipz-surface">Edit</button>
                <button onClick={() => { setMenuOpen(false); onDelete(profile.id); }} className="w-full px-3 py-1.5 text-[11px] text-left text-rose-400 hover:bg-clipz-surface">Delete</button>
              </div>
            )}
          </div>
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

function ProfileFormDialog({
  isOpen,
  onClose,
  initial,
  title,
  onSave,
  isLoading,
}: {
  isOpen: boolean;
  onClose: () => void;
  initial: typeof defaultForm;
  title: string;
  onSave: (data: any) => void;
  isLoading: boolean;
}) {
  const [form, setForm] = useState(initial);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[90dvh] overflow-y-auto rounded-xl border border-clipz-border bg-clipz-panel shadow-2xl">
        <div className="sticky top-0 flex items-center justify-between border-b border-clipz-border-soft bg-clipz-panel p-4 z-10">
          <div>
            <h3 className="text-[14px] font-semibold text-white">{title}</h3>
            <p className="text-[11px] text-clipz-text-muted">{form.name || "New profile"}</p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
            <X size={16} />
          </button>
        </div>
        <div className="p-4 space-y-5">
          <div>
            <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
              <Target size={14} className="text-clipz-accent-soft" /> Basic Information
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="block text-[11px] text-clipz-text-muted mb-1">Profile Name *</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. Gaming Highlights"
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                />
              </div>
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Profile Type</label>
                <select
                  value={form.type}
                  onChange={(e) => setForm({ ...form, type: e.target.value as ProfileType })}
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                >
                  <option value="creator">Creator Channel</option>
                  <option value="general">General Channel</option>
                  <option value="topic">Topic Channel</option>
                  <option value="manual">Manual Channel</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Image URL</label>
                <input
                  type="text"
                  value={form.image}
                  onChange={(e) => setForm({ ...form, image: e.target.value })}
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-[11px] text-clipz-text-muted mb-1">Description</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="What is this profile for?"
                  rows={2}
                  className="w-full rounded-md border border-clipz-border bg-clipz-surface px-2.5 py-1.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50 resize-none"
                />
              </div>
            </div>
          </div>
          <div>
            <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
              <Globe size={14} className="text-emerald-400" /> Target Platforms
            </h4>
            <div className="flex flex-wrap gap-2">
              {allPlatforms.map((p) => {
                const active = form.targetPlatforms.includes(p);
                return (
                  <button
                    key={p}
                    onClick={() =>
                      setForm({
                        ...form,
                        targetPlatforms: active
                          ? form.targetPlatforms.filter((x) => x !== p)
                          : [...form.targetPlatforms, p],
                      })
                    }
                    className={`rounded-md border px-2.5 py-1 text-[11px] font-medium transition-colors ${
                      active ? "bg-clipz-accent/15 text-clipz-accent-soft border-clipz-accent/30" : "bg-clipz-surface text-clipz-text-muted border-clipz-border hover:text-white"
                    }`}
                  >
                    {active && <Check size={12} className="inline mr-1" />}
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
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Min Length (s)</label>
                <input
                  type="number"
                  value={form.clipLengths.min}
                  onChange={(e) => setForm({ ...form, clipLengths: { ...form.clipLengths, min: Number(e.target.value) } })}
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                />
              </div>
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Max Length (s)</label>
                <input
                  type="number"
                  value={form.clipLengths.max}
                  onChange={(e) => setForm({ ...form, clipLengths: { ...form.clipLengths, max: Number(e.target.value) } })}
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                />
              </div>
            </div>
          </div>
          <div>
            <h4 className="text-[12px] font-semibold text-white mb-3 flex items-center gap-2">
              <Shield size={14} className="text-rose-400" /> Rights & Safety
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Rights Status</label>
                <select
                  value={form.rightsStatus}
                  onChange={(e) => setForm({ ...form, rightsStatus: e.target.value })}
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                >
                  <option value="owned">Owned</option>
                  <option value="licensed">Licensed</option>
                  <option value="creator-approved">Creator Approved</option>
                  <option value="transformative-review">Transformative Review</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Safety Level</label>
                <select
                  value={form.safetyLevel}
                  onChange={(e) => setForm({ ...form, safetyLevel: e.target.value })}
                  className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                >
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div className="sticky bottom-0 flex items-center justify-end gap-2 border-t border-clipz-border-soft bg-clipz-panel p-4">
          <button onClick={onClose} className="rounded-md border border-clipz-border px-3 py-1.5 text-[12px] text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
            Cancel
          </button>
          <button
            onClick={() => onSave(form)}
            disabled={!form.name || isLoading}
            className="rounded-md bg-clipz-accent px-3 py-1.5 text-[12px] font-medium text-white hover:bg-clipz-accent/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {isLoading && <Loader2 size={12} className="animate-spin" />}
            {isLoading ? "Saving..." : "Save Profile"}
          </button>
        </div>
      </div>
    </div>
  );
}

export function ProfilesPage() {
  const [filter, setFilter] = useState<ProfileType | "all">("all");
  const [search, setSearch] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingProfile, setEditingProfile] = useState<FProfileView | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const { data: profilesData, isLoading, error } = useProfileList({ pageSize: 50 });
  const createProfile = useCreateProfile();
  const updateProfile = useUpdateProfile();
  const deleteProfile = useDeleteProfile();

  const profiles = profilesData?.data || [];

  const filtered = profiles.filter((p) => {
    if (filter !== "all" && p.profileType !== filter) return false;
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const showToast = (message: string, type: "success" | "error") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleCreate = async (data: any) => {
    try {
      await createProfile.mutateAsync(data);
      setShowCreateDialog(false);
      showToast("Profile created successfully", "success");
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to create profile", "error");
    }
  };

  const handleUpdate = async (data: any) => {
    if (!editingProfile) return;
    try {
      await updateProfile.mutateAsync({ id: editingProfile.id, data });
      setEditingProfile(null);
      showToast("Profile updated successfully", "success");
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to update profile", "error");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteProfile.mutateAsync(id);
      showToast("Profile deleted", "success");
    } catch (err: any) {
      showToast(err?.error?.message || "Failed to delete profile", "error");
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 lg:p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-64 bg-clipz-surface rounded" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-[280px] bg-clipz-panel rounded-xl border border-clipz-border" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {toast && (
        <div className={`fixed top-4 right-4 z-[100] rounded-lg px-4 py-2 text-[12px] font-medium shadow-lg ${
          toast.type === "success" ? "bg-emerald-600 text-white" : "bg-rose-600 text-white"
        }`}>
          {toast.message}
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Creator Profiles</h2>
          <p className="text-[12px] text-clipz-text-muted">Manage clip profiles, sources, targets, and preferences</p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90 transition-colors glow-accent"
        >
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

      {profiles.length === 0 ? (
        <div className="rounded-xl border border-dashed border-clipz-border bg-clipz-panel/50 p-12 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-clipz-surface border border-clipz-border mx-auto mb-4">
            <Users size={28} className="text-clipz-text-dim" />
          </div>
          <h3 className="text-[15px] font-semibold text-white mb-1">No profiles yet</h3>
          <p className="text-[12px] text-clipz-text-muted mb-6 max-w-sm mx-auto">
            Create your first profile to start clipping and publishing content across platforms.
          </p>
          <button
            onClick={() => setShowCreateDialog(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-clipz-accent px-4 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90 transition-colors"
          >
            <Plus size={14} />
            Create Your First Profile
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-clipz-border bg-clipz-panel/50 p-12 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-clipz-surface border border-clipz-border mx-auto mb-4">
            <Search size={28} className="text-clipz-text-dim" />
          </div>
          <h3 className="text-[15px] font-semibold text-white mb-1">No matching profiles</h3>
          <p className="text-[12px] text-clipz-text-muted mb-6">
            Try a different filter or search term.
          </p>
          <button onClick={() => { setFilter("all"); setSearch(""); }} className="text-[12px] text-clipz-accent-soft hover:text-white">
            Clear filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((profile) => (
            <ProfileCard key={profile.id} profile={profile} onEdit={setEditingProfile} onDelete={handleDelete} />
          ))}
        </div>
      )}

      <ProfileFormDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        initial={defaultForm}
        title="Create New Profile"
        onSave={handleCreate}
        isLoading={createProfile.isPending}
      />

      {editingProfile && (
        <ProfileFormDialog
          isOpen={!!editingProfile}
          onClose={() => setEditingProfile(null)}
          initial={{
            name: editingProfile.name,
            type: editingProfile.type,
            description: editingProfile.description,
            image: editingProfile.image,
            targetPlatforms: editingProfile.targetPlatforms,
            clipLengths: editingProfile.clipLengths,
            contentThemes: editingProfile.contentThemes,
            rightsStatus: editingProfile.rightsStatus,
            safetyLevel: editingProfile.safetyLevel,
            autoApproval: editingProfile.autoApproval,
            sourceChannels: editingProfile.sourceChannels,
            postingSchedule: editingProfile.postingSchedule,
          }}
          title="Edit Profile"
          onSave={handleUpdate}
          isLoading={updateProfile.isPending}
        />
      )}
    </div>
  );
}