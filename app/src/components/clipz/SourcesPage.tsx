"use client";

import { useState } from "react";
import {
  Upload,
  Link as LinkIcon,
  Search,
  MoreHorizontal,
  Play,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Film,
} from "lucide-react";
import { sourceVideos, SourceStatus } from "../../lib/mock-data";

const statusLabels: Record<SourceStatus, string> = {
  validating: "Validating",
  queued: "Queued",
  transcribing: "Transcribing",
  analyzing: "Analyzing",
  candidates_ready: "Candidates Ready",
  processed: "Processed",
  failed: "Failed",
};

const statusColors: Record<SourceStatus, string> = {
  validating: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  queued: "bg-zinc-500/15 text-zinc-400 border-zinc-500/20",
  transcribing: "bg-cyan-500/15 text-cyan-400 border-cyan-500/20",
  analyzing: "bg-violet-500/15 text-violet-400 border-violet-500/20",
  candidates_ready: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  processed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  failed: "bg-rose-500/15 text-rose-400 border-rose-500/20",
};

function formatDuration(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m ${Math.floor(seconds % 60)}s`;
}

function StatusBadge({ status }: { status: SourceStatus }) {
  const isProcessing = ["transcribing", "analyzing", "validating"].includes(status);
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[10px] font-medium ${statusColors[status]}`}>
      {isProcessing && <Loader2 size={10} className="animate-spin" />}
      {status === "failed" && <AlertCircle size={10} />}
      {status === "candidates_ready" && <CheckCircle2 size={10} />}
      {statusLabels[status]}
    </span>
  );
}

function ProgressBar({ progress, color = "#7c5cff" }: { progress: number; color?: string }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full progress-track">
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${progress}%`, backgroundColor: color }} />
    </div>
  );
}

export function SourcesPage() {
  const [filter, setFilter] = useState<SourceStatus | "all">("all");
  const [search, setSearch] = useState("");
  const [view, setView] = useState<"table" | "grid">("table");

  const filtered = sourceVideos.filter((s) => {
    if (filter !== "all" && s.status !== filter) return false;
    if (search && !s.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const stats = {
    total: sourceVideos.length,
    processing: sourceVideos.filter((s) => ["transcribing", "analyzing", "validating"].includes(s.status)).length,
    ready: sourceVideos.filter((s) => s.status === "candidates_ready" || s.status === "processed").length,
    failed: sourceVideos.filter((s) => s.status === "failed").length,
    totalDuration: sourceVideos.reduce((acc, s) => acc + s.duration, 0),
  };

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Source Library</h2>
          <p className="text-[12px] text-clipz-text-muted">{stats.total} sources · {formatDuration(stats.totalDuration)} of footage</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 rounded-lg border border-clipz-border bg-clipz-surface px-3 py-2 text-[12px] text-white hover:bg-clipz-elevated transition-colors">
            <LinkIcon size={14} /> Add URL
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90 transition-colors glow-accent">
            <Upload size={14} /> Upload
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-clipz-text-muted mb-1">
            <Film size={12} /> Total Sources
          </div>
          <p className="text-2xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-violet-400 mb-1">
            <Loader2 size={12} className="animate-spin" /> Processing
          </div>
          <p className="text-2xl font-bold text-white">{stats.processing}</p>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-emerald-400 mb-1">
            <CheckCircle2 size={12} /> Ready
          </div>
          <p className="text-2xl font-bold text-white">{stats.ready}</p>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-rose-400 mb-1">
            <AlertCircle size={12} /> Failed
          </div>
          <p className="text-2xl font-bold text-white">{stats.failed}</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div className="flex items-center gap-1.5 flex-wrap">
          {(["all", "candidates_ready", "analyzing", "transcribing", "queued", "failed"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`shrink-0 rounded-lg px-2.5 py-1.5 text-[11px] font-medium transition-all ${
                filter === s ? "bg-clipz-accent text-white" : "bg-clipz-surface border border-clipz-border text-clipz-text-muted hover:text-white"
              }`}
            >
              {s === "all" ? "All" : statusLabels[s]}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 sm:ml-auto w-full sm:w-auto">
          <div className="relative flex-1 sm:flex-none sm:w-64">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-clipz-text-dim" />
            <input
              type="text"
              placeholder="Search sources..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full h-8 rounded-lg border border-clipz-border bg-clipz-surface pl-8 pr-3 text-[12px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50"
            />
          </div>
          <div className="flex rounded-lg border border-clipz-border overflow-hidden">
            <button
              onClick={() => setView("table")}
              className={`p-2 ${view === "table" ? "bg-clipz-accent text-white" : "text-clipz-text-muted hover:text-white"}`}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M3 9h18M9 21V9" />
              </svg>
            </button>
            <button
              onClick={() => setView("grid")}
              className={`p-2 ${view === "grid" ? "bg-clipz-accent text-white" : "text-clipz-text-muted hover:text-white"}`}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="3" width="7" height="7" rx="1" />
                <rect x="3" y="14" width="7" height="7" rx="1" />
                <rect x="14" y="14" width="7" height="7" rx="1" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {view === "table" && (
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="border-b border-clipz-border text-left text-clipz-text-muted">
                  <th className="py-3 px-4 font-medium">Source</th>
                  <th className="py-3 px-4 font-medium">Profile</th>
                  <th className="py-3 px-4 font-medium">Status</th>
                  <th className="py-3 px-4 font-medium w-32">Progress</th>
                  <th className="py-3 px-4 font-medium">Duration</th>
                  <th className="py-3 px-4 font-medium">Resolution</th>
                  <th className="py-3 px-4 font-medium">Size</th>
                  <th className="py-3 px-4 font-medium w-10"></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((source) => (
                  <tr key={source.id} className="border-b border-clipz-border-soft hover:bg-clipz-surface/50 transition-colors cursor-pointer">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-16 shrink-0 rounded-md overflow-hidden relative bg-clipz-elevated group">
                          <img src={source.thumbnail} alt="" className="h-full w-full object-cover" />
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <Play size={14} className="text-white" fill="white" />
                          </div>
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-white truncate max-w-[240px]">{source.title}</p>
                          <p className="text-[10px] text-clipz-text-dim truncate max-w-[240px]">{source.filename}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-clipz-text-muted">
                      {source.profileId === "p1" ? "Kai Cenat" : source.profileId === "p2" ? "Clip District" : source.profileId === "p3" ? "Tech Insights" : source.profileId === "p4" ? "Comedy Hub" : "Manual"}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={source.status} />
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1"><ProgressBar progress={source.progress} /></div>
                        <span className="text-[11px] text-clipz-text-muted w-8 text-right">{source.progress}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-clipz-text-muted font-mono text-[11px]">{formatDuration(source.duration)}</td>
                    <td className="py-3 px-4 text-clipz-text-muted font-mono text-[11px]">{source.resolution}</td>
                    <td className="py-3 px-4 text-clipz-text-muted text-[11px]">{source.fileSize}</td>
                    <td className="py-3 px-4">
                      <button className="p-1 rounded text-clipz-text-dim hover:text-white hover:bg-clipz-elevated">
                        <MoreHorizontal size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {view === "grid" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((source) => (
            <div key={source.id} className="group rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden hover:border-clipz-accent/40 transition-all cursor-pointer">
              <div className="relative aspect-video bg-clipz-elevated">
                <img src={source.thumbnail} alt="" className="h-full w-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                <div className="absolute top-2 left-2"><StatusBadge status={source.status} /></div>
                <div className="absolute bottom-2 right-2 rounded bg-black/70 px-1.5 py-0.5 text-[10px] text-white font-mono">
                  {formatDuration(source.duration)}
                </div>
                {["transcribing", "analyzing", "validating"].includes(source.status) && (
                  <div className="absolute bottom-2 left-2 right-2"><ProgressBar progress={source.progress} /></div>
                )}
              </div>
              <div className="p-3">
                <p className="text-[12px] font-medium text-white truncate">{source.title}</p>
                <div className="flex items-center justify-between mt-1.5 text-[10px] text-clipz-text-dim">
                  <span>{source.resolution} · {source.fps}fps</span>
                  <span>{source.fileSize}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
