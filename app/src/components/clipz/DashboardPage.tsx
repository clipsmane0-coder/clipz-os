"use client";

import { useState, useEffect } from "react";
import { Link } from "@tanstack/react-router";
import {
  TrendingUp,
  Video,
  Scissors,
  Clock,
  Play,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  Eye,
  ThumbsUp,
  MessageSquare,
  Share2,
  ArrowUpRight,
  ArrowDownRight,
  HardDrive,
  Cpu,
  Zap,
  Activity,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
} from "recharts";
import {
  totals,
  analyticsData,
  sourceVideos,
  renderJobs,
  candidateClips,
  scheduledPosts,
  profiles,
  hookTypeStats,
} from "../../lib/mock-data";

function StatCard({
  label,
  value,
  change,
  changeUp = true,
  icon,
  accent = "violet",
}: {
  label: string;
  value: string;
  change?: string;
  changeUp?: boolean;
  icon: React.ReactNode;
  accent?: "violet" | "cyan" | "green" | "amber" | "pink";
}) {
  const accentColors = {
    violet: "from-violet-500/20 to-violet-500/5 text-violet-400 border-violet-500/20",
    cyan: "from-cyan-500/20 to-cyan-500/5 text-cyan-400 border-cyan-500/20",
    green: "from-emerald-500/20 to-emerald-500/5 text-emerald-400 border-emerald-500/20",
    amber: "from-amber-500/20 to-amber-500/5 text-amber-400 border-amber-500/20",
    pink: "from-pink-500/20 to-pink-500/5 text-pink-400 border-pink-500/20",
  };

  return (
    <div className="group relative overflow-hidden rounded-xl border border-clipz-border bg-clipz-panel p-4 transition-all hover:border-clipz-border/80 hover:bg-clipz-surface/50">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-medium text-clipz-text-muted uppercase tracking-wider">
            {label}
          </p>
          <p className="mt-1.5 text-2xl font-bold text-white tracking-tight">
            {value}
          </p>
          {change && (
            <div className={`mt-1 flex items-center gap-1 text-[11px] ${changeUp ? "text-emerald-400" : "text-rose-400"}`}>
              {changeUp ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
              {change}
              <span className="text-clipz-text-dim">vs last week</span>
            </div>
          )}
        </div>
        <div
          className={`flex h-9 w-9 items-center justify-center rounded-lg border bg-gradient-to-br ${accentColors[accent]}`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}

function MiniSparkline({ data, color = "#7c5cff" }: { data: number[]; color?: string }) {
  return (
    <div className="h-8 w-20">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data.map((v, i) => ({ v, i }))}>
          <defs>
            <linearGradient id={`grad-${color}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.4} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="v"
            stroke={color}
            strokeWidth={1.5}
            fill={`url(#grad-${color})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    candidates_ready: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    processed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    analyzing: "bg-violet-500/15 text-violet-400 border-violet-500/20",
    transcribing: "bg-cyan-500/15 text-cyan-400 border-cyan-500/20",
    queued: "bg-amber-500/15 text-amber-400 border-amber-500/20",
    validating: "bg-amber-500/15 text-amber-400 border-amber-500/20",
    failed: "bg-rose-500/15 text-rose-400 border-rose-500/20",
    rendering: "bg-violet-500/15 text-violet-400 border-violet-500/20",
    completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    urgent: "bg-rose-500/15 text-rose-400 border-rose-500/20",
    high: "bg-amber-500/15 text-amber-400 border-amber-500/20",
    normal: "bg-zinc-500/15 text-zinc-400 border-zinc-500/20",
    low: "bg-zinc-500/15 text-zinc-400 border-zinc-500/20",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-medium capitalize ${styles[status] || styles.normal}`}
    >
      {status.replace("_", " ")}
    </span>
  );
}

function ProgressBar({ progress, color = "#7c5cff" }: { progress: number; color?: string }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full progress-track">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${progress}%`, backgroundColor: color }}
      />
    </div>
  );
}

export function DashboardPage() {
  const [liveProgress, setLiveProgress] = useState(67);

  useEffect(() => {
    const t = setInterval(() => {
      setLiveProgress((p) => (p >= 100 ? 0 : p + 0.3));
    }, 300);
    return () => clearInterval(t);
  }, []);

  const viewsData = analyticsData.map((d) => ({
    date: d.date.slice(5),
    views: d.views / 1000,
    clips: d.clipsPosted,
    engagement: (d.likes + d.comments + d.shares) / 10,
  }));

  const activeRender = renderJobs.find((j) => j.status === "rendering");
  const newCandidates = candidateClips.filter((c) => c.status === "new");
  const processingSources = sourceVideos.filter(
    (s) => !["processed", "failed", "candidates_ready"].includes(s.status)
  );

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Good afternoon, Operator</h2>
          <p className="text-[12px] text-clipz-text-muted">
            {totals.sourcesProcessing} sources processing, {totals.candidatesReady} candidates ready for review
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select className="h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-clipz-text-muted focus:outline-none focus:border-clipz-accent/50">
            <option>Last 14 days</option>
            <option>Last 7 days</option>
            <option>Last 30 days</option>
            <option>This month</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
        <StatCard label="Total Views" value={totals.totalViews} change="+12.4%" icon={<Eye size={16} />} accent="violet" />
        <StatCard label="Clips Published" value={totals.clipsPublished.toString()} change="+18.2%" icon={<Scissors size={16} />} accent="cyan" />
        <StatCard label="This Week" value={totals.clipsThisWeek.toString()} change="+4.1%" icon={<TrendingUp size={16} />} accent="green" />
        <StatCard label="Avg. Completion" value={totals.avgCompletionRate} change="+2.8%" icon={<CheckCircle2 size={16} />} accent="amber" />
        <StatCard label="Candidates" value={totals.candidatesReady.toString()} change="+7" icon={<Zap size={16} />} accent="pink" />
        <StatCard label="Storage Used" value={totals.storageUsed} icon={<HardDrive size={16} />} accent="violet" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
            <div>
              <h3 className="text-[13px] font-semibold text-white">Performance Overview</h3>
              <p className="text-[11px] text-clipz-text-muted">Views and engagement over time</p>
            </div>
            <div className="flex items-center gap-3 text-[11px]">
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-violet-500" />
                <span className="text-clipz-text-muted">Views (K)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-cyan-400" />
                <span className="text-clipz-text-muted">Engagement</span>
              </div>
            </div>
          </div>
          <div className="h-[280px] p-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={viewsData}>
                <defs>
                  <linearGradient id="viewsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#7c5cff" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#7c5cff" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="engGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1b24" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={{ stroke: "#1a1b24" }} tickLine={false} />
                <YAxis tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={false} tickLine={false} width={40} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#12131a", border: "1px solid #23242f", borderRadius: "8px", fontSize: "11px", color: "#e6e7ee" }}
                  labelStyle={{ color: "#8b8d98", fontSize: "10px", marginBottom: "4px" }}
                  itemStyle={{ fontSize: "11px" }}
                />
                <Area type="monotone" dataKey="views" stroke="#7c5cff" strokeWidth={2} fill="url(#viewsGrad)" />
                <Area type="monotone" dataKey="engagement" stroke="#22d3ee" strokeWidth={2} fill="url(#engGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-[13px] font-semibold text-white">System Status</h3>
              <Activity size={14} className="text-clipz-accent-soft" />
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-clipz-text-muted">GPU Utilization</span>
                  <span className="text-white font-medium">{totals.gpuUtilization}%</span>
                </div>
                <ProgressBar progress={totals.gpuUtilization} color="#7c5cff" />
              </div>
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-clipz-text-muted">CPU Utilization</span>
                  <span className="text-white font-medium">{totals.cpuUtilization}%</span>
                </div>
                <ProgressBar progress={totals.cpuUtilization} color="#22d3ee" />
              </div>
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-clipz-text-muted">Storage</span>
                  <span className="text-white font-medium">34.2%</span>
                </div>
                <ProgressBar progress={34.2} color="#34d399" />
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-clipz-border-soft">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-clipz-green pulse-dot" />
                  <span className="text-[11px] text-clipz-text-muted">
                    {totals.errorCount === 0 ? "All systems operational" : `${totals.errorCount} error`}
                  </span>
                </div>
                <span className="text-[10px] text-clipz-text-dim font-mono">RTX 4090 · 64GB</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
            <h3 className="text-[13px] font-semibold text-white mb-3">Top Hook Types</h3>
            <div className="space-y-2.5">
              {hookTypeStats.slice(0, 5).map((h, i) => (
                <div key={h.type} className="flex items-center gap-3">
                  <span className="text-[11px] text-clipz-text-dim font-mono w-4">{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between text-[11px] mb-0.5">
                      <span className="text-white truncate">{h.type}</span>
                      <span className="text-clipz-accent-soft font-medium">
                        {(h.avgViews / 1000).toFixed(0)}K
                      </span>
                    </div>
                    <ProgressBar
                      progress={(h.avgViews / 71000) * 100}
                      color={i === 0 ? "#7c5cff" : i === 1 ? "#22d3ee" : "#34d399"}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
            <div>
              <h3 className="text-[13px] font-semibold text-white">Active Render</h3>
              <p className="text-[11px] text-clipz-text-muted">
                {renderJobs.filter((j) => j.status === "rendering").length} rendering · {renderJobs.filter((j) => j.status === "queued").length} queued
              </p>
            </div>
            <Link to="/queue" className="text-[11px] text-clipz-accent-soft hover:text-white flex items-center gap-0.5">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          <div className="p-4 space-y-3">
            {activeRender && (
              <div className="rounded-lg border border-clipz-accent/30 bg-clipz-accent/5 p-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="min-w-0">
                    <p className="text-[12px] font-medium text-white truncate">{activeRender.clipTitle}</p>
                    <p className="text-[10px] text-clipz-text-muted">{activeRender.renderPreset} · {activeRender.device}</p>
                  </div>
                  <StatusBadge status="rendering" />
                </div>
                <div className="flex items-center justify-between text-[10px] text-clipz-text-muted mb-1">
                  <span>{Math.round(liveProgress)}%</span>
                  <span>{activeRender.estimatedTime}</span>
                </div>
                <ProgressBar progress={liveProgress} color="#7c5cff" />
              </div>
            )}
            {renderJobs.filter((j) => j.status === "queued").slice(0, 3).map((job) => (
              <div key={job.id} className="flex items-center justify-between rounded-lg border border-clipz-border-soft bg-clipz-surface/50 p-2.5">
                <div className="min-w-0 flex-1">
                  <p className="text-[12px] text-white truncate">{job.clipTitle}</p>
                  <p className="text-[10px] text-clipz-text-dim">{job.renderPreset}</p>
                </div>
                <StatusBadge status={job.priority} />
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
            <div>
              <h3 className="text-[13px] font-semibold text-white">Processing Sources</h3>
              <p className="text-[11px] text-clipz-text-muted">{processingSources.length} in progress</p>
            </div>
            <Link to="/sources" className="text-[11px] text-clipz-accent-soft hover:text-white flex items-center gap-0.5">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-clipz-border-soft">
            {processingSources.slice(0, 4).map((source) => (
              <div key={source.id} className="p-3 flex items-center gap-3 hover:bg-clipz-surface/30 transition-colors">
                <div className="h-10 w-16 shrink-0 rounded-md bg-clipz-elevated overflow-hidden relative">
                  <img src={source.thumbnail} alt="" className="h-full w-full object-cover opacity-70" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-white font-medium truncate">{source.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <StatusBadge status={source.status} />
                    <span className="text-[10px] text-clipz-text-dim">{Math.floor(source.duration / 60)}m</span>
                  </div>
                </div>
                <div className="w-14 text-right">
                  <span className="text-[11px] text-clipz-accent-soft font-medium">{source.progress}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
            <div>
              <h3 className="text-[13px] font-semibold text-white">New Candidates</h3>
              <p className="text-[11px] text-clipz-text-muted">{newCandidates.length} clips awaiting review</p>
            </div>
            <Link to="/clip-lab" className="text-[11px] text-clipz-accent-soft hover:text-white flex items-center gap-0.5">
              Clip Lab <ChevronRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-clipz-border-soft">
            {newCandidates.slice(0, 4).map((clip) => (
              <Link key={clip.id} to="/clip-lab" className="flex items-center gap-3 p-3 hover:bg-clipz-surface/30 transition-colors block">
                <div className="relative h-10 w-16 shrink-0 rounded-md overflow-hidden">
                  <img src={clip.thumbnail} alt="" className="h-full w-full object-cover" />
                  <div className="absolute bottom-0.5 right-0.5 rounded bg-black/70 px-1 text-[9px] text-white font-medium">
                    {Math.round(clip.duration)}s
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-white font-medium truncate">{clip.title}</p>
                  <p className="text-[10px] text-clipz-text-dim truncate">{clip.hook}</p>
                </div>
                <div className="flex flex-col items-end gap-0.5">
                  <span className={`text-[12px] font-bold ${clip.score >= 85 ? "text-emerald-400" : clip.score >= 70 ? "text-amber-400" : "text-rose-400"}`}>
                    {clip.score}
                  </span>
                  <span className="text-[9px] text-clipz-text-dim uppercase">score</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
          <div>
            <h3 className="text-[13px] font-semibold text-white">Profile Overview</h3>
            <p className="text-[11px] text-clipz-text-muted">Performance across active profiles</p>
          </div>
          <Link to="/profiles" className="text-[11px] text-clipz-accent-soft hover:text-white flex items-center gap-0.5">
            Manage profiles <ChevronRight size={12} />
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x lg:divide-x divide-clipz-border-soft">
          {profiles.filter((p) => p.status === "active").slice(0, 3).map((profile) => (
            <div key={profile.id} className="p-4">
              <div className="flex items-center gap-3 mb-3">
                <img src={profile.image} alt="" className="h-10 w-10 rounded-lg object-cover" />
                <div className="min-w-0 flex-1">
                  <p className="text-[13px] font-semibold text-white truncate">{profile.name}</p>
                  <p className="text-[10px] text-clipz-text-dim capitalize">{profile.type} channel</p>
                </div>
                <div className="h-2 w-2 rounded-full bg-clipz-green pulse-dot" />
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div>
                  <p className="text-[14px] font-bold text-white">{profile.clipsPublished}</p>
                  <p className="text-[9px] text-clipz-text-dim uppercase">Published</p>
                </div>
                <div>
                  <p className="text-[14px] font-bold text-clipz-accent-soft">{profile.clipsQueued}</p>
                  <p className="text-[9px] text-clipz-text-dim uppercase">Queued</p>
                </div>
                <div>
                  <p className="text-[14px] font-bold text-cyan-400">{profile.targetPlatforms.length}</p>
                  <p className="text-[9px] text-clipz-text-dim uppercase">Platforms</p>
                </div>
              </div>
              <MiniSparkline data={[12, 19, 15, 25, 22, 30, 28, 35, 32, 42, 38, 45]} color="#7c5cff" />
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
          <div>
            <h3 className="text-[13px] font-semibold text-white">Upcoming Schedule</h3>
            <p className="text-[11px] text-clipz-text-muted">{scheduledPosts.length} posts scheduled this week</p>
          </div>
          <Link to="/calendar" className="text-[11px] text-clipz-accent-soft hover:text-white flex items-center gap-0.5">
            View calendar <ChevronRight size={12} />
          </Link>
        </div>
        <div className="p-4 overflow-x-auto">
          <div className="flex gap-3 min-w-max">
            {scheduledPosts.slice(0, 7).map((post) => (
              <div key={post.id} className="w-32 shrink-0 rounded-lg border border-clipz-border-soft bg-clipz-surface/50 overflow-hidden group hover:border-clipz-accent/30 transition-all cursor-pointer">
                <div className="relative h-44 w-full bg-clipz-elevated">
                  <img src={post.thumbnail} alt="" className="h-full w-full object-cover opacity-90 group-hover:opacity-100 transition-opacity" />
                  <div className="absolute top-1.5 left-1.5">
                    <span className="rounded bg-black/70 px-1.5 py-0.5 text-[9px] font-medium text-white backdrop-blur-sm">
                      {post.platform}
                    </span>
                  </div>
                </div>
                <div className="p-2">
                  <p className="text-[11px] text-white font-medium truncate">{post.clipTitle}</p>
                  <p className="text-[9px] text-clipz-text-dim mt-0.5">{post.scheduledDate.slice(5)} · {post.scheduledTime}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
