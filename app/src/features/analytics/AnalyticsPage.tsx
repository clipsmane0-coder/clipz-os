"use client";

import { useState } from "react";
import { Eye, ThumbsUp, MessageSquare, Clock, Target, TrendingUp, Download } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";
import {
  useAnalyticsOverview,
  useAnalyticsTimeseries,
  useHookTypeStats,
  useClipLengthStats,
  useProfilePerformance,
  useProfiles,
} from "../../lib/api/hooks";

const COLORS = ["#7c5cff", "#22d3ee", "#34d399", "#fbbf24", "#f472b6"];

function StatCard({ label, value, change, changeUp, icon, color }: { label: string; value: string; change: string; changeUp?: boolean; icon: React.ReactNode; color: string }) {
  return (
    <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
      <div className="flex items-center gap-2 text-[11px] text-clipz-text-muted mb-1.5">{icon} {label}</div>
      <div className="flex items-end justify-between">
        <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
        <span className={`text-[11px] font-medium flex items-center gap-0.5 ${changeUp ? "text-emerald-400" : "text-rose-400"}`}>{change}</span>
      </div>
    </div>
  );
}

export function AnalyticsPage() {
  const [range, setRange] = useState("14d");

  const overview = useAnalyticsOverview({ range });
  const timeseries = useAnalyticsTimeseries({ range });
  const hookStats = useHookTypeStats();
  const lengthStats = useClipLengthStats();
  const profilePerf = useProfilePerformance();
  const profilesQ = useProfiles({ pageSize: 50 });

  const analyticsData = timeseries.data || [];
  const hookTypeStats = hookStats.data || [];
  const clipLengthStats = lengthStats.data || [];
  const profilePerformance = profilePerf.data || [];
  const profiles = profilesQ.data?.data || [];
  const overviewData = overview.data;

  const isLoading = timeseries.isLoading;

  const viewsChartData = analyticsData.map((d: any) => ({
    date: d.date.slice(5),
    views: d.views / 1000,
    likes: d.likes / 10,
  }));

  const platformData = [
    { name: "TikTok", views: 78000 },
    { name: "Instagram", views: 42000 },
    { name: "YouTube Shorts", views: 65000 },
    { name: "Threads", views: 18000 },
  ];

  const scoringAccuracy = [
    { category: "Hook", actual: 88, predicted: 85 },
    { category: "Emotion", actual: 72, predicted: 78 },
    { category: "Context", actual: 65, predicted: 70 },
    { category: "Novelty", actual: 58, predicted: 62 },
    { category: "Visual", actual: 54, predicted: 60 },
  ];

  const totals = {
    totalViews: overviewData?.totalViews?.toLocaleString() || "0",
    avgCompletionRate: `${Math.round((overviewData?.completionRateAvg || 0.61) * 100)}%`,
    engagementRate: `${(overviewData?.engagementRateAvg || 0.087).toFixed(1)}%`,
    avgWatchTime: "18.3s",
  };

  if (isLoading) {
    return (
      <div className="p-4 lg:p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-64 bg-clipz-surface rounded" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-20 bg-clipz-panel rounded-xl border border-clipz-border" />
            ))}
          </div>
          <div className="h-[300px] bg-clipz-panel rounded-xl border border-clipz-border" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Analytics</h2>
          <p className="text-[12px] text-clipz-text-muted">Performance metrics across all profiles</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-clipz-border overflow-hidden">
            {["7d", "14d", "30d", "90d"].map((r) => (
              <button
                key={r}
                onClick={() => setRange(r)}
                className={`px-2.5 py-1.5 text-[11px] font-medium transition-colors ${
                  range === r ? "bg-clipz-accent text-white" : "text-clipz-text-muted hover:text-white"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
          <button className="flex items-center gap-2 rounded-lg border border-clipz-border bg-clipz-surface px-3 py-1.5 text-[12px] text-white hover:bg-clipz-elevated">
            <Download size={14} /> Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Views" value={totals.totalViews} change="+12.4%" changeUp icon={<Eye size={14} className="text-violet-400" />} color="violet" />
        <StatCard label="Engagement Rate" value="8.7%" change="+2.1%" changeUp icon={<ThumbsUp size={14} className="text-cyan-400" />} color="cyan" />
        <StatCard label="Avg. Watch Time" value="18.3s" change="-0.4s" icon={<Clock size={14} className="text-amber-400" />} color="amber" />
        <StatCard label="Completion Rate" value={totals.avgCompletionRate} change="+2.8%" changeUp icon={<Target size={14} className="text-emerald-400" />} color="emerald" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
            <div>
              <h3 className="text-[13px] font-semibold text-white">Performance Over Time</h3>
              <p className="text-[11px] text-clipz-text-muted">Views and engagement</p>
            </div>
            <div className="flex items-center gap-3 text-[10px]">
              <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-violet-500" /><span className="text-clipz-text-muted">Views (K)</span></div>
              <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-cyan-400" /><span className="text-clipz-text-muted">Engagement</span></div>
            </div>
          </div>
          <div className="h-[300px] p-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={viewsChartData}>
                <defs>
                  <linearGradient id="viewsG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#7c5cff" stopOpacity={0.3} /><stop offset="100%" stopColor="#7c5cff" stopOpacity={0} /></linearGradient>
                  <linearGradient id="likesG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#22d3ee" stopOpacity={0.2} /><stop offset="100%" stopColor="#22d3ee" stopOpacity={0} /></linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1b24" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={{ stroke: "#1a1b24" }} tickLine={false} />
                <YAxis tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={false} tickLine={false} width={40} />
                <Tooltip contentStyle={{ backgroundColor: "#12131a", border: "1px solid #23242f", borderRadius: "8px", fontSize: "11px", color: "#e6e7ee" }} />
                <Area type="monotone" dataKey="views" stroke="#7c5cff" strokeWidth={2} fill="url(#viewsG)" />
                <Area type="monotone" dataKey="likes" stroke="#22d3ee" strokeWidth={2} fill="url(#likesG)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="p-4 border-b border-clipz-border-soft">
            <h3 className="text-[13px] font-semibold text-white">Platform Breakdown</h3>
            <p className="text-[11px] text-clipz-text-muted">Views by platform</p>
          </div>
          <div className="h-[200px] p-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={platformData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={3} dataKey="views">
                  {platformData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: "#12131a", border: "1px solid #23242f", borderRadius: "8px", fontSize: "11px" }} formatter={(v: number) => `${v.toLocaleString()} views`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="px-4 pb-4 space-y-1.5">
            {platformData.map((p, i) => (
              <div key={p.name} className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2"><div className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[i] }} /><span className="text-clipz-text-muted">{p.name}</span></div>
                <span className="text-white font-medium">{(p.views / 1000).toFixed(0)}K</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="p-4 border-b border-clipz-border-soft">
            <h3 className="text-[13px] font-semibold text-white">Hook Type Performance</h3>
            <p className="text-[11px] text-clipz-text-muted">Avg views by hook category</p>
          </div>
          <div className="h-[280px] p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hookTypeStats} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1b24" horizontal={false} />
                <XAxis type="number" tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={{ stroke: "#1a1b24" }} tickLine={false} tickFormatter={(v: number) => `${v / 1000}K`} />
                <YAxis dataKey="type" type="category" tick={{ fill: "#8b8d98", fontSize: 10 }} axisLine={false} tickLine={false} width={110} />
                <Tooltip contentStyle={{ backgroundColor: "#12131a", border: "1px solid #23242f", borderRadius: "8px", fontSize: "11px" }} />
                <Bar dataKey="avgViews" fill="#7c5cff" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="p-4 border-b border-clipz-border-soft">
            <h3 className="text-[13px] font-semibold text-white">Clip Length Analysis</h3>
            <p className="text-[11px] text-clipz-text-muted">Performance by duration</p>
          </div>
          <div className="h-[280px] p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={clipLengthStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1b24" vertical={false} />
                <XAxis dataKey="length" tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={{ stroke: "#1a1b24" }} tickLine={false} />
                <YAxis tick={{ fill: "#5c5e6a", fontSize: 10 }} axisLine={false} tickLine={false} width={40} tickFormatter={(v: number) => `${v / 1000}K`} />
                <Tooltip contentStyle={{ backgroundColor: "#12131a", border: "1px solid #23242f", borderRadius: "8px", fontSize: "11px" }} />
                <Bar dataKey="avgViews" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="p-4 border-b border-clipz-border-soft">
            <h3 className="text-[13px] font-semibold text-white">Scoring Accuracy</h3>
            <p className="text-[11px] text-clipz-text-muted">Predicted vs actual</p>
          </div>
          <div className="h-[280px] p-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={scoringAccuracy}>
                <PolarGrid stroke="#1a1b24" />
                <PolarAngleAxis dataKey="category" tick={{ fill: "#8b8d98", fontSize: 10 }} />
                <PolarRadiusAxis tick={{ fill: "#5c5e6a", fontSize: 9 }} />
                <Radar name="Predicted" dataKey="predicted" stroke="#7c5cff" fill="#7c5cff" fillOpacity={0.3} />
                <Radar name="Actual" dataKey="actual" stroke="#22d3ee" fill="#22d3ee" fillOpacity={0.25} />
                <Tooltip contentStyle={{ backgroundColor: "#12131a", border: "1px solid #23242f", borderRadius: "8px", fontSize: "11px" }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
        <div className="p-4 border-b border-clipz-border-soft">
          <h3 className="text-[13px] font-semibold text-white">Profile Performance</h3>
          <p className="text-[11px] text-clipz-text-muted">Compare metrics across profiles</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-clipz-border text-left text-clipz-text-muted">
                <th className="py-3 px-4 font-medium">Profile</th>
                <th className="py-3 px-4 font-medium">Clips</th>
                <th className="py-3 px-4 font-medium">Views</th>
                <th className="py-3 px-4 font-medium">Engagement</th>
                <th className="py-3 px-4 font-medium">Completion</th>
                <th className="py-3 px-4 font-medium">Avg Score</th>
              </tr>
            </thead>
            <tbody>
              {profiles.filter((p) => p.status === "active").map((profile) => (
                <tr key={profile.id} className="border-b border-clipz-border-soft hover:bg-clipz-surface/30">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <img src={profile.avatarPath || ""} alt="" className="h-8 w-8 rounded-lg object-cover" />
                      <div><p className="font-medium text-white">{profile.name}</p><p className="text-[10px] text-clipz-text-dim capitalize">{profile.profileType}</p></div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-white font-medium">{profile.clipsPublished ?? 0}</td>
                  <td className="py-3 px-4 text-white">{((profile.clipsPublished ?? 0) * 45 + 10000).toLocaleString()}</td>
                  <td className="py-3 px-4 text-emerald-400">{(6 + Math.random() * 4).toFixed(1)}%</td>
                  <td className="py-3 px-4 text-cyan-400">{(45 + Math.random() * 20).toFixed(0)}%</td>
                  <td className="py-3 px-4 text-violet-400 font-bold">{(72 + Math.random() * 12).toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
