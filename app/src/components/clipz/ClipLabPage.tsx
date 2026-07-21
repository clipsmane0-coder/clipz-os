"use client";

import { useState, useEffect } from "react";
import {
  Play,
  Pause,
  Check,
  X,
  Scissors,
  Sparkles,
  Volume2,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  ThumbsUp,
  AlertTriangle,
  Film,
  Download,
  Type,
  Crop,
  Tag,
  Hash,
} from "lucide-react";
import { useCandidateList, useSourceList } from "../../lib/api/hooks";
import type { FCandidateView } from "../../lib/api/mapper";

function ScoreBar({ label, value, max = 20, color = "#7c5cff" }: { label: string; value: number; max?: number; color?: string }) {
  return (
    <div>
      <div className="flex justify-between text-[10px] mb-0.5">
        <span className="text-clipz-text-muted">{label}</span>
        <span className="text-white font-medium">{value}</span>
      </div>
      <div className="h-1.5 w-full rounded-full progress-track">
        <div className="h-full rounded-full" style={{ width: `${(value / max) * 100}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

function CandidateCard({ clip, selected, onClick }: { clip: FCandidateView; selected: boolean; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`group relative rounded-lg border overflow-hidden cursor-pointer transition-all ${
        selected ? "border-clipz-accent shadow-lg shadow-violet-500/10" : "border-clipz-border-soft hover:border-clipz-border"
      }`}
    >
      <div className="relative aspect-video bg-clipz-elevated">
        <img src={clip.thumbnail} alt="" className="h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute top-2 left-2 flex items-center gap-1.5">
          <div className={`h-1.5 w-1.5 rounded-full ${clip.overallScore >= 85 ? "bg-emerald-400" : clip.overallScore >= 70 ? "bg-amber-400" : "bg-rose-400"}`} />
          <span className={`text-[10px] font-bold ${clip.overallScore >= 85 ? "text-emerald-400" : clip.overallScore >= 70 ? "text-amber-400" : "text-rose-400"}`}>
            {clip.overallScore}
          </span>
        </div>
        <div className="absolute bottom-1.5 right-1.5 rounded bg-black/70 px-1 py-0.5 text-[9px] text-white font-mono">
          {Math.round(clip.duration)}s
        </div>
        {selected && <div className="absolute inset-0 border-2 border-clipz-accent rounded-lg pointer-events-none" />}
      </div>
      <div className="p-2.5">
        <p className="text-[11px] font-medium text-white truncate">{clip.title}</p>
        <p className="text-[10px] text-clipz-text-dim truncate mt-0.5">{clip.hook}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-[9px] text-clipz-text-dim uppercase">{clip.recommendedPlatform}</span>
          <span className="flex items-center gap-1 text-[9px] text-clipz-accent-soft">
            <Sparkles size={10} /> New
          </span>
        </div>
      </div>
    </div>
  );
}

export function ClipLabPage() {
  const [selectedId, setSelectedId] = useState<string>("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [playhead, setPlayhead] = useState(0);
  const [activeTab, setActiveTab] = useState<"scoring" | "caption" | "crop" | "metadata">("scoring");

  const { data: candidatesData, isLoading: candidatesLoading } = useCandidateList({ pageSize: 50 });
  const { data: sourcesData, isLoading: sourcesLoading } = useSourceList({ pageSize: 50 });
  const candidateClips = candidatesData?.data || [];
  const sourceVideos = sourcesData?.data || [];

  const isLoading = candidatesLoading || sourcesLoading;

  // Set initial selected candidate
  if (!isLoading && !selectedId && candidateClips.length > 0) {
    setSelectedId(candidateClips[0].id);
  }

  const selected = candidateClips.find((c) => c.id === selectedId);
  const source = sourceVideos.find((s) => s.id === selected?.sourceId);

  useEffect(() => {
    if (!isPlaying || !selected) return;
    const t = setInterval(() => {
      setPlayhead((p) => {
        if (p >= 100) { setIsPlaying(false); return 0; }
        return p + (100 / selected.duration) * 0.1;
      });
    }, 100);
    return () => clearInterval(t);
  }, [isPlaying, selected?.duration, selected?.id]);

  const formatTime = (pct: number) => {
    const current = selected ? (pct / 100) * selected.duration : 0;
    const m = Math.floor(current / 60);
    const s = Math.floor(current % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  if (isLoading || !selected) {
    return (
      <div className="flex h-[calc(100dvh-3.5rem)]">
        <div className="w-72 border-r border-clipz-border bg-clipz-panel/50 p-4 animate-pulse">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-20 bg-clipz-surface rounded-lg mb-2" />
          ))}
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-clipz-text-dim text-sm">Loading Clip Lab...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100dvh-3.5rem)] overflow-hidden">
      {/* Left sidebar */}
      <div className="hidden md:flex w-[280px] shrink-0 flex-col border-r border-clipz-border bg-clipz-panel">
        <div className="p-3 border-b border-clipz-border-soft">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-[13px] font-semibold text-white">Candidate Clips</h3>
            <span className="rounded-md bg-clipz-accent/15 text-clipz-accent-soft px-1.5 py-0.5 text-[10px] font-medium">
              {candidateClips.length}
            </span>
          </div>
          <input
            type="text"
            placeholder="Search candidates..."
            className="w-full h-7 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[11px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50"
          />
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
          {candidateClips.map((clip) => (
            <CandidateCard
              key={clip.id}
              clip={clip}
              selected={clip.id === selectedId}
              onClick={() => { setSelectedId(clip.id); setPlayhead(0); setIsPlaying(false); }}
            />
          ))}
        </div>
      </div>

      {/* Center: player */}
      <div className="flex-1 flex flex-col min-w-0 bg-clipz-bg">
        <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden">
          <img src={selected.thumbnail} alt="" className="absolute inset-0 w-full h-full object-cover opacity-80" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />

          <div className="absolute top-4 left-4 right-4 flex items-start justify-between">
            <div>
              <p className="text-[12px] text-white/80">{source?.title}</p>
              <p className="text-[14px] font-semibold text-white mt-0.5">{selected.title}</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-1.5 rounded-md bg-black/40 text-white hover:bg-black/60 backdrop-blur-sm">
                <Volume2 size={14} />
              </button>
              <button className="p-1.5 rounded-md bg-black/40 text-white hover:bg-black/60 backdrop-blur-sm">
                <Maximize2 size={14} />
              </button>
            </div>
          </div>

          <button onClick={() => setIsPlaying(!isPlaying)} className="relative z-10 h-16 w-16 rounded-full bg-white/20 backdrop-blur-md border border-white/30 flex items-center justify-center hover:bg-white/30 transition-all group">
            {isPlaying ? <Pause size={24} className="text-white" fill="white" /> : <Play size={24} className="text-white ml-1" fill="white" />}
          </button>

          <div className="absolute bottom-0 left-0 right-0 p-4">
            <div className="relative mb-3">
              <div className="h-1.5 w-full rounded-full bg-white/20">
                <div className="h-full rounded-full bg-clipz-accent" style={{ width: `${playhead}%` }} />
              </div>
              <div className="absolute top-0 h-full rounded-l-full border-l-2 border-emerald-400" style={{ left: "0%" }} />
              <div className="absolute top-0 h-full rounded-r-full border-r-2 border-rose-400" style={{ left: "100%" }} />
              {[15, 35, 52, 70, 88].map((m) => (
                <div key={m} className="absolute top-0 h-full w-px bg-white/20" style={{ left: `${m}%` }} />
              ))}
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button onClick={() => setIsPlaying(!isPlaying)} className="p-1.5 text-white hover:text-clipz-accent-soft">
                  {isPlaying ? <Pause size={18} /> : <Play size={18} />}
                </button>
                <button className="p-1.5 text-white/70 hover:text-white"><ChevronLeft size={16} /></button>
                <button className="p-1.5 text-white/70 hover:text-white"><ChevronRight size={16} /></button>
                <span className="text-[11px] text-white font-mono">{formatTime(playhead)} / {formatTime(100)}</span>
              </div>
              <select className="h-7 rounded-md bg-black/40 border border-white/20 px-2 text-[10px] text-white backdrop-blur-sm focus:outline-none">
                <option>1x</option><option>1.5x</option><option>2x</option><option>0.5x</option>
              </select>
            </div>
          </div>
        </div>

        {/* Timeline strip */}
        <div className="h-20 border-t border-clipz-border bg-clipz-panel p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-clipz-text-muted">Waveform</span>
            <div className="flex items-center gap-1.5">
              <span className="flex items-center gap-1 text-[9px] text-emerald-400"><div className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> In</span>
              <span className="flex items-center gap-1 text-[9px] text-rose-400"><div className="h-1.5 w-1.5 rounded-full bg-rose-400" /> Out</span>
            </div>
          </div>
          <div className="relative h-10 flex items-center gap-px">
            {Array.from({ length: 80 }).map((_, i) => {
              const h = 20 + Math.abs(Math.sin(i * 0.3) * 20) + Math.random() * 10;
              return <div key={i} className="flex-1 rounded-sm bg-clipz-accent/60" style={{ height: `${h}%` }} />;
            })}
          </div>
        </div>

        {/* Action bar */}
        <div className="flex items-center justify-between border-t border-clipz-border bg-clipz-panel px-4 py-3">
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 rounded-md border border-rose-500/30 bg-rose-500/10 px-3 py-1.5 text-[12px] text-rose-400 hover:bg-rose-500/20">
              <X size={14} /> Reject
            </button>
            <button className="flex items-center gap-1.5 rounded-md border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-[12px] text-amber-400 hover:bg-amber-500/20">
              <Scissors size={14} /> Adjust
            </button>
            <button className="flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-[12px] text-emerald-400 hover:bg-emerald-500/20">
              <Check size={14} /> Approve
            </button>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 rounded-md border border-clipz-border bg-clipz-surface px-3 py-1.5 text-[12px] text-white hover:bg-clipz-elevated">
              <Download size={14} /> Export
            </button>
            <button className="flex items-center gap-1.5 rounded-md bg-clipz-accent px-3.5 py-1.5 text-[12px] font-medium text-white hover:bg-clipz-accent/90">
              <Film size={14} /> Send to Render
            </button>
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="hidden lg:flex w-[320px] shrink-0 flex-col border-l border-clipz-border bg-clipz-panel">
        <div className="flex border-b border-clipz-border-soft">
          {[
            { id: "scoring", label: "Scoring", icon: <Sparkles size={12} /> },
            { id: "caption", label: "Caption", icon: <Type size={12} /> },
            { id: "crop", label: "Crop", icon: <Crop size={12} /> },
            { id: "metadata", label: "Meta", icon: <Tag size={12} /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex-1 flex items-center justify-center gap-1 px-2 py-2.5 text-[11px] font-medium border-b-2 transition-colors ${
                activeTab === tab.id ? "text-white border-clipz-accent bg-clipz-accent/5" : "text-clipz-text-muted border-transparent hover:text-white"
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          {activeTab === "scoring" && (
            <>
              <div className="text-center">
                <div className={`text-5xl font-bold mb-1 ${selected.overallScore >= 85 ? "text-emerald-400" : selected.overallScore >= 70 ? "text-amber-400" : "text-rose-400"}`}>
                  {selected.overallScore}
                </div>
                <p className="text-[11px] text-clipz-text-muted">Clip Score / 100</p>
              </div>

              <div className="space-y-2.5">
                <h4 className="text-[11px] font-semibold text-white">Score Breakdown</h4>
                <ScoreBar label="Hook Strength" value={selected.scoreBreakdown.hook_strength} max={20} color="#7c5cff" />
                <ScoreBar label="Context Completeness" value={selected.scoreBreakdown.context_completeness} max={15} color="#22d3ee" />
                <ScoreBar label="Emotional Intensity" value={selected.scoreBreakdown.emotional_intensity} max={15} color="#f472b6" />
                <ScoreBar label="Profile Match" value={selected.scoreBreakdown.profile_match} max={15} color="#34d399" />
                <ScoreBar label="Payoff Strength" value={selected.scoreBreakdown.payoff_strength} max={10} color="#fbbf24" />
                <ScoreBar label="Visual Activity" value={selected.scoreBreakdown.visual_activity} max={10} color="#a78bfa" />
                <ScoreBar label="Topic Relevance" value={selected.scoreBreakdown.topic_relevance} max={5} color="#38bdf8" />
              </div>

              <div className="space-y-2">
                <h4 className="text-[11px] font-semibold text-white">Why it was selected</h4>
                <ul className="space-y-1.5">
                  {selected.whySelected.map((reason, i) => (
                    <li key={i} className="flex items-start gap-2 text-[11px] text-clipz-text-muted">
                      <Check size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {selected.riskFlags.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-[11px] font-semibold text-white flex items-center gap-1.5">
                    <AlertTriangle size={12} className="text-amber-400" /> Risk Flags
                  </h4>
                  {selected.riskFlags.map((flag, i) => (
                    <div key={i} className="text-[11px] text-amber-400 rounded-md bg-amber-500/5 border border-amber-500/10 px-2 py-1.5">
                      {flag}
                    </div>
                  ))}
                </div>
              )}

              <div className="grid grid-cols-3 gap-2">
                <div className="rounded-lg bg-clipz-surface p-2.5 text-center">
                  <p className="text-[13px] font-bold text-emerald-400">{Math.round(selected.cropConfidence * 100)}%</p>
                  <p className="text-[9px] text-clipz-text-dim">Crop</p>
                </div>
                <div className="rounded-lg bg-clipz-surface p-2.5 text-center">
                  <p className="text-[13px] font-bold text-cyan-400">{Math.round(selected.audioQuality * 100)}%</p>
                  <p className="text-[9px] text-clipz-text-dim">Audio</p>
                </div>
                <div className="rounded-lg bg-clipz-surface p-2.5 text-center">
                  <p className="text-[13px] font-bold text-violet-400">{Math.round(selected.visualQuality * 100)}%</p>
                  <p className="text-[9px] text-clipz-text-dim">Visual</p>
                </div>
              </div>
            </>
          )}

          {activeTab === "caption" && (
            <div className="space-y-4">
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2">Caption Preset</h4>
                <div className="grid grid-cols-2 gap-2">
                  {["Clean", "Streamer", "Podcast", "Bold Viral", "Minimal", "Gaming"].map((p, i) => (
                    <button
                      key={p}
                      className={`rounded-md border px-2 py-1.5 text-[11px] ${
                        i === 1 ? "bg-clipz-accent/15 text-clipz-accent-soft border-clipz-accent/30" : "bg-clipz-surface text-clipz-text-muted border-clipz-border hover:text-white"
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2">Suggested Caption</h4>
                <p className="text-[12px] text-white bg-clipz-surface rounded-lg p-3 border border-clipz-border leading-relaxed">
                  {selected.suggestedCaption}
                </p>
              </div>
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2 flex items-center gap-1.5">
                  <Hash size={12} className="text-clipz-accent-soft" /> Hashtags
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {selected.suggestedHashtags.map((tag) => (
                    <span key={tag} className="rounded-md bg-clipz-surface border border-clipz-border px-2 py-0.5 text-[10px] text-clipz-accent-soft">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2">Transcript</h4>
                <div className="max-h-40 overflow-y-auto rounded-lg bg-clipz-surface border border-clipz-border p-3 space-y-1.5">
                  {selected.transcript.split(". ").map((line, i) => (
                    <div key={i} className="text-[11px] text-clipz-text-muted">
                      <span className="text-clipz-text-dim font-mono mr-2 text-[10px]">
                        {(i * 4).toString().padStart(2, "0")}:00
                      </span>
                      {line.trim()}.
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "crop" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <h4 className="text-[11px] font-semibold text-white">Crop Mode</h4>
                {[
                  { name: "Face Tracking", desc: "Keeps primary face in safe zone" },
                  { name: "Center Crop", desc: "Simple centered framing" },
                  { name: "Speaker Switching", desc: "Moves with active speaker" },
                  { name: "Split Screen", desc: "Two-person layout" },
                ].map((mode, i) => (
                  <button
                    key={mode.name}
                    className={`w-full flex items-center gap-3 rounded-lg border p-2.5 text-left ${
                      i === 0 ? "bg-clipz-accent/10 border-clipz-accent/30" : "bg-clipz-surface border-clipz-border hover:border-clipz-border/80"
                    }`}
                  >
                    <div className={`h-8 w-8 rounded-md flex items-center justify-center ${i === 0 ? "bg-clipz-accent/20" : "bg-clipz-elevated"}`}>
                      <Crop size={14} className={i === 0 ? "text-clipz-accent-soft" : "text-clipz-text-dim"} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-[12px] font-medium ${i === 0 ? "text-white" : "text-clipz-text-muted"}`}>{mode.name}</p>
                      <p className="text-[10px] text-clipz-text-dim">{mode.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h4 className="text-[11px] font-semibold text-white">Crop Confidence</h4>
                  <span className="text-[11px] text-emerald-400 font-medium">{Math.round(selected.cropConfidence * 100)}%</span>
                </div>
                <div className="h-2 rounded-full progress-track">
                  <div className="h-full rounded-full bg-emerald-400" style={{ width: `${selected.cropConfidence * 100}%` }} />
                </div>
              </div>
            </div>
          )}

          {activeTab === "metadata" && (
            <div className="space-y-4">
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2">Clip Title</h4>
                <input type="text" defaultValue={selected.title} className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface px-2.5 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50" />
              </div>
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2">Hook</h4>
                <p className="text-[12px] text-white italic bg-clipz-surface rounded-lg p-3 border border-clipz-border">{selected.hook}</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <h4 className="text-[11px] font-semibold text-white mb-2">Start</h4>
                  <div className="flex items-center gap-1 rounded-md border border-clipz-border bg-clipz-surface px-2 h-8 font-mono text-[12px] text-white">
                    {Math.floor(selected.startTime / 60)}:{(selected.startTime % 60).toFixed(1).padStart(4, "0")}
                  </div>
                </div>
                <div>
                  <h4 className="text-[11px] font-semibold text-white mb-2">End</h4>
                  <div className="flex items-center gap-1 rounded-md border border-clipz-border bg-clipz-surface px-2 h-8 font-mono text-[12px] text-white">
                    {Math.floor(selected.endTime / 60)}:{(selected.endTime % 60).toFixed(1).padStart(4, "0")}
                  </div>
                </div>
              </div>
              <div>
                <h4 className="text-[11px] font-semibold text-white mb-2">Platform</h4>
                <div className="flex gap-2">
                  {["TikTok", "Instagram", "YouTube Shorts"].map((p) => (
                    <button
                      key={p}
                      className={`rounded-md border px-2 py-1 text-[10px] ${
                        p === selected.recommendedPlatform ? "bg-clipz-accent/15 text-clipz-accent-soft border-clipz-accent/30" : "bg-clipz-surface text-clipz-text-muted border-clipz-border hover:text-white"
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
