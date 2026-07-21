"use client";

import { useState } from "react";
import {
  Play,
  Pause,
  CheckCircle2,
  Loader2,
  AlertTriangle,
  Clock,
  ArrowUp,
  ArrowDown,
  RotateCcw,
  Trash2,
  Zap,
  Cpu,
  HardDrive,
  Search,
} from "lucide-react";
import { renderJobs, RenderJob } from "../../lib/mock-data";

const priorityStyles = {
  urgent: "bg-rose-500/15 text-rose-400 border-rose-500/20",
  high: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  normal: "bg-zinc-500/15 text-zinc-400 border-zinc-500/20",
  low: "bg-zinc-500/10 text-zinc-500 border-zinc-500/15",
};

const statusStyles = {
  queued: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  rendering: "bg-violet-500/15 text-violet-400 border-violet-500/20",
  completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  failed: "bg-rose-500/15 text-rose-400 border-rose-500/20",
};

function ProgressBar({ progress, color = "#7c5cff" }: { progress: number; color?: string }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full progress-track">
      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${progress}%`, backgroundColor: color }} />
    </div>
  );
}

export function QueuePage() {
  const [filter, setFilter] = useState<RenderJob["status"] | "all">("all");

  const filtered = renderJobs.filter((j) => filter === "all" || j.status === filter);

  const stats = {
    rendering: renderJobs.filter((j) => j.status === "rendering").length,
    queued: renderJobs.filter((j) => j.status === "queued").length,
    completed: renderJobs.filter((j) => j.status === "completed").length,
    failed: renderJobs.filter((j) => j.status === "failed").length,
  };

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Render Queue</h2>
          <p className="text-[12px] text-clipz-text-muted">
            {stats.rendering} rendering · {stats.queued} queued · {stats.completed} completed
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 rounded-lg border border-clipz-border bg-clipz-surface px-3 py-2 text-[12px] text-white hover:bg-clipz-elevated">
            <Pause size={14} /> Pause All
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90">
            <Play size={14} /> Start Queue
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2"><Zap size={16} className="text-violet-400" /><span className="text-[12px] font-medium text-white">GPU</span></div>
            <span className="text-[10px] text-emerald-400 flex items-center gap-1">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 pulse-dot" /> Active
            </span>
          </div>
          <div className="flex items-end justify-between mb-1">
            <span className="text-2xl font-bold text-white">67%</span>
            <span className="text-[10px] text-clipz-text-dim">RTX 4090</span>
          </div>
          <ProgressBar progress={67} color="#7c5cff" />
          <div className="mt-2 flex justify-between text-[10px] text-clipz-text-dim">
            <span>{stats.rendering} active job</span>
            <span>65C</span>
          </div>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2"><Cpu size={16} className="text-cyan-400" /><span className="text-[12px] font-medium text-white">CPU</span></div>
            <span className="text-[10px] text-emerald-400 flex items-center gap-1">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 pulse-dot" /> Ready
            </span>
          </div>
          <div className="flex items-end justify-between mb-1">
            <span className="text-2xl font-bold text-white">41%</span>
            <span className="text-[10px] text-clipz-text-dim">Ryzen 9 7950X</span>
          </div>
          <ProgressBar progress={41} color="#22d3ee" />
          <div className="mt-2 flex justify-between text-[10px] text-clipz-text-dim">
            <span>2 queued jobs</span>
            <span>58C</span>
          </div>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2"><HardDrive size={16} className="text-emerald-400" /><span className="text-[12px] font-medium text-white">Storage</span></div>
            <span className="text-[10px] text-amber-400">34% used</span>
          </div>
          <div className="flex items-end justify-between mb-1">
            <span className="text-2xl font-bold text-white">342GB</span>
            <span className="text-[10px] text-clipz-text-dim">of 1TB</span>
          </div>
          <ProgressBar progress={34.2} color="#34d399" />
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div className="flex items-center gap-1.5">
          {(["all", "rendering", "queued", "completed", "failed"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`shrink-0 rounded-lg px-2.5 py-1.5 text-[11px] font-medium transition-all capitalize ${
                filter === s ? "bg-clipz-accent text-white" : "bg-clipz-surface border border-clipz-border text-clipz-text-muted hover:text-white"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <div className="sm:ml-auto relative w-full sm:w-64">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-clipz-text-dim" />
          <input
            type="text"
            placeholder="Search jobs..."
            className="w-full h-8 rounded-lg border border-clipz-border bg-clipz-surface pl-8 pr-3 text-[12px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50"
          />
        </div>
      </div>

      <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-clipz-border text-left text-clipz-text-muted">
                <th className="py-3 px-4 font-medium w-8"></th>
                <th className="py-3 px-4 font-medium">Job</th>
                <th className="py-3 px-4 font-medium">Status</th>
                <th className="py-3 px-4 font-medium">Priority</th>
                <th className="py-3 px-4 font-medium w-48">Progress</th>
                <th className="py-3 px-4 font-medium">Preset</th>
                <th className="py-3 px-4 font-medium">Device</th>
                <th className="py-3 px-4 font-medium">ETA</th>
                <th className="py-3 px-4 font-medium w-12"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((job) => (
                <tr key={job.id} className="border-b border-clipz-border-soft hover:bg-clipz-surface/50">
                  <td className="py-3 px-4">
                    <div className="flex flex-col gap-1">
                      <button className="text-clipz-text-dim hover:text-white"><ArrowUp size={12} /></button>
                      <button className="text-clipz-text-dim hover:text-white"><ArrowDown size={12} /></button>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-16 shrink-0 rounded-md overflow-hidden bg-clipz-elevated">
                        <img src={`https://picsum.photos/seed/${job.id}/100/60`} alt="" className="h-full w-full object-cover" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-white truncate max-w-[280px]">{job.clipTitle}</p>
                        <p className="text-[10px] text-clipz-text-dim">{job.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[10px] font-medium capitalize ${statusStyles[job.status]}`}>
                      {job.status === "rendering" && <Loader2 size={10} className="animate-spin" />}
                      {job.status === "completed" && <CheckCircle2 size={10} />}
                      {job.status === "failed" && <AlertTriangle size={10} />}
                      {job.status === "queued" && <Clock size={10} />}
                      {job.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[10px] font-medium capitalize ${priorityStyles[job.priority]}`}>
                      {job.priority}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1">
                        <ProgressBar
                          progress={job.progress}
                          color={job.status === "failed" ? "#f87171" : job.status === "completed" ? "#34d399" : "#7c5cff"}
                        />
                      </div>
                      <span className="text-[11px] text-clipz-text-muted w-10 text-right font-mono">{job.progress}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-clipz-text-muted">{job.renderPreset}</td>
                  <td className="py-3 px-4 text-clipz-text-muted text-[11px]">{job.device}</td>
                  <td className="py-3 px-4 text-clipz-text-muted text-[11px]">{job.estimatedTime}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1">
                      {job.status === "failed" && (
                        <button className="p-1 text-amber-400 hover:text-amber-300 hover:bg-amber-500/10 rounded">
                          <RotateCcw size={13} />
                        </button>
                      )}
                      <button className="p-1 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded">
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {stats.failed > 0 && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/5 overflow-hidden">
          <div className="flex items-center gap-2 p-3 border-b border-rose-500/20">
            <AlertTriangle size={16} className="text-rose-400" />
            <span className="text-[12px] font-medium text-rose-300">Render failure detected</span>
            <span className="ml-auto text-[11px] text-rose-400">2 retries attempted</span>
          </div>
          <div className="p-4">
            <div className="rounded-lg bg-black/30 border border-rose-500/10 p-3 font-mono text-[11px] text-clipz-text-muted">
              <p><span className="text-rose-400">ERROR</span> FONT_NOT_FOUND</p>
              <p className="mt-1 text-clipz-text-dim">
                Caption font 'Montserrat Bold' missing from system. Select another caption font.
              </p>
            </div>
            <div className="mt-3 flex gap-2">
              <button className="rounded-md bg-clipz-accent px-3 py-1.5 text-[11px] font-medium text-white hover:bg-clipz-accent/90">
                Change Caption Font
              </button>
              <button className="rounded-md border border-clipz-border bg-clipz-surface px-3 py-1.5 text-[11px] text-white hover:bg-clipz-elevated">
                View Full Log
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
