"use client";

import { useState } from "react";
import { Search, Play, Eye, ThumbsUp, MessageSquare, Grid, List } from "lucide-react";
import { candidateClips, CandidateClip } from "../../lib/mock-data";

const statusColors = {
  approved: "bg-violet-500/15 text-violet-400 border-violet-500/20",
  rendered: "bg-cyan-500/15 text-cyan-400 border-cyan-500/20",
  scheduled: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  published: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  archived: "bg-zinc-500/15 text-zinc-400 border-zinc-500/20",
  new: "bg-pink-500/15 text-pink-400 border-pink-500/20",
};

const statusLabels: Record<string, string> = {
  approved: "Approved",
  rendered: "Rendered",
  scheduled: "Scheduled",
  published: "Published",
  archived: "Archived",
  new: "New",
  reviewing: "Reviewing",
  rendering: "Rendering",
};

const allClips: (CandidateClip & { views?: number; likes?: number; comments?: number; platform?: string })[] = [
  ...candidateClips.map((c, i) => ({
    ...c,
    status: i % 4 === 0 ? "published" : i % 4 === 1 ? "scheduled" : i % 4 === 2 ? "rendered" : "approved",
    views: i * 12500 + Math.floor(Math.random() * 50000),
    likes: Math.floor((i * 12500 + Math.floor(Math.random() * 50000)) * 0.07),
    comments: Math.floor((i * 12500 + Math.floor(Math.random() * 50000)) * 0.012),
    platform: ["TikTok", "Instagram", "YouTube Shorts", "Threads"][i % 4],
  })),
  ...candidateClips.slice(0, 6).map((c, i) => ({
    ...c,
    id: `${c.id}-b`,
    status: "published" as const,
    views: 80000 + i * 35000,
    likes: Math.floor((80000 + i * 35000) * 0.08),
    comments: Math.floor((80000 + i * 35000) * 0.015),
    platform: ["TikTok", "Instagram", "YouTube Shorts", "Threads"][i % 4],
  })),
];

function formatNumber(n: number) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}

export function LibraryPage() {
  const [view, setView] = useState<"grid" | "list">("grid");
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  const filtered = allClips.filter((c) => {
    if (filter !== "all" && c.status !== filter) return false;
    if (search && !c.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const totalViews = allClips.filter((c) => c.status === "published").reduce((acc, c) => acc + (c.views || 0), 0);

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Content Library</h2>
          <p className="text-[12px] text-clipz-text-muted">{allClips.length} clips · {formatNumber(totalViews)} total views</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div className="flex items-center gap-1.5 flex-wrap">
          {["all", "published", "scheduled", "rendered", "approved", "archived"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`shrink-0 rounded-lg px-2.5 py-1.5 text-[11px] font-medium transition-all capitalize ${
                filter === f ? "bg-clipz-accent text-white" : "bg-clipz-surface border border-clipz-border text-clipz-text-muted hover:text-white"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 sm:ml-auto w-full sm:w-auto">
          <div className="relative flex-1 sm:flex-none sm:w-64">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-clipz-text-dim" />
            <input
              type="text"
              placeholder="Search clips..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full h-8 rounded-lg border border-clipz-border bg-clipz-surface pl-8 pr-3 text-[12px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50"
            />
          </div>
          <div className="flex rounded-lg border border-clipz-border overflow-hidden">
            <button onClick={() => setView("grid")} className={`p-2 ${view === "grid" ? "bg-clipz-accent text-white" : "text-clipz-text-muted hover:text-white"}`}>
              <Grid size={14} />
            </button>
            <button onClick={() => setView("list")} className={`p-2 ${view === "list" ? "bg-clipz-accent text-white" : "text-clipz-text-muted hover:text-white"}`}>
              <List size={14} />
            </button>
          </div>
        </div>
      </div>

      {view === "grid" && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
          {filtered.map((clip) => (
            <div key={clip.id} className="group rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden hover:border-clipz-accent/40 transition-all cursor-pointer">
              <div className="relative aspect-[9/16] bg-clipz-elevated">
                <img src={clip.thumbnail} alt="" className="h-full w-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
                <div className="absolute top-2 left-2">
                  <span className={`inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-medium capitalize ${statusColors[clip.status as keyof typeof statusColors] || statusColors.new}`}>
                    {statusLabels[clip.status] || clip.status}
                  </span>
                </div>
                <div className="absolute top-2 right-2 rounded bg-black/60 px-1 py-0.5 text-[9px] text-white font-mono backdrop-blur-sm">
                  {Math.round(clip.duration)}s
                </div>
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="h-10 w-10 rounded-full bg-white/20 backdrop-blur-md border border-white/30 flex items-center justify-center">
                    <Play size={16} className="text-white ml-0.5" fill="white" />
                  </div>
                </div>
                {clip.views !== undefined && (
                  <div className="absolute bottom-2 left-2 right-2 flex items-center gap-2 text-[9px] text-white/80">
                    <span className="flex items-center gap-0.5"><Eye size={10} /> {formatNumber(clip.views)}</span>
                    <span className="flex items-center gap-0.5"><ThumbsUp size={10} /> {formatNumber(clip.likes || 0)}</span>
                  </div>
                )}
              </div>
              <div className="p-2.5">
                <p className="text-[11px] font-medium text-white line-clamp-2 leading-snug h-8">{clip.title}</p>
                <div className="flex items-center justify-between mt-1.5">
                  <span className="text-[9px] text-clipz-text-dim">{clip.platform || clip.recommendedPlatform}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {view === "list" && (
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="border-b border-clipz-border text-left text-clipz-text-muted">
                  <th className="py-3 px-4 font-medium w-12"></th>
                  <th className="py-3 px-4 font-medium">Clip</th>
                  <th className="py-3 px-4 font-medium">Status</th>
                  <th className="py-3 px-4 font-medium">Platform</th>
                  <th className="py-3 px-4 font-medium">Duration</th>
                  <th className="py-3 px-4 font-medium">Score</th>
                  <th className="py-3 px-4 font-medium">Views</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((clip) => (
                  <tr key={clip.id} className="border-b border-clipz-border-soft hover:bg-clipz-surface/50 cursor-pointer">
                    <td className="py-2.5 px-4">
                      <div className="h-8 w-14 rounded overflow-hidden bg-clipz-elevated">
                        <img src={clip.thumbnail} alt="" className="h-full w-full object-cover" />
                      </div>
                    </td>
                    <td className="py-2.5 px-4 font-medium text-white truncate max-w-[280px]">{clip.title}</td>
                    <td className="py-2.5 px-4">
                      <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[10px] font-medium capitalize ${statusColors[clip.status as keyof typeof statusColors] || statusColors.new}`}>
                        {statusLabels[clip.status] || clip.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-clipz-text-muted">{clip.platform || clip.recommendedPlatform}</td>
                    <td className="py-2.5 px-4 text-clipz-text-muted font-mono text-[11px]">{Math.round(clip.duration)}s</td>
                    <td className="py-2.5 px-4">
                      <span className={`text-[12px] font-bold ${clip.score >= 85 ? "text-emerald-400" : clip.score >= 70 ? "text-amber-400" : "text-rose-400"}`}>
                        {clip.score}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-clipz-text-muted">{clip.views !== undefined ? formatNumber(clip.views) : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
