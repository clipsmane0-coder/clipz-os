"use client";

import { useSource, useSourceTranscript, useSourceScenes, useCandidateList } from "../../lib/api/hooks";
import { composeSourceView } from "../../lib/api/view-models";
import { Link } from "@tanstack/react-router";
import { ArrowLeft, Film, Clock, Activity, FileText, BarChart3 } from "lucide-react";

export function SourceDetail({ sourceId }: { sourceId: string }) {
  const { data: sourceData, isLoading, error } = useSource(sourceId);
  const { data: transcriptData } = useSourceTranscript(sourceId);
  const { data: scenesData } = useSourceScenes(sourceId);
  const { data: candidatesData } = useCandidateList({ sourceId, pageSize: 10 });

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

  if (error || !sourceData) {
    return (
      <div className="p-4 lg:p-6">
        <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-8 text-center">
          <Film size={40} className="mx-auto mb-3 text-rose-400" />
          <h3 className="text-[15px] font-semibold text-white mb-1">Source Not Found</h3>
          <p className="text-[12px] text-clipz-text-muted mb-4">The source video you're looking for doesn't exist or was removed.</p>
          <Link to="/sources" className="inline-flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white">
            <ArrowLeft size={14} /> Back to Sources
          </Link>
        </div>
      </div>
    );
  }

  const view = composeSourceView(sourceData);
  const transcripts = transcriptData;
  const scenes = scenesData || [];
  const candidates = candidatesData?.data || [];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex items-center gap-2">
        <Link to="/sources" className="p-1.5 rounded-md text-clipz-text-muted hover:text-white hover:bg-clipz-surface">
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h2 className="text-lg font-semibold text-white">{view.title}</h2>
          <p className="text-[11px] text-clipz-text-muted">{view.filename}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-clipz-text-muted mb-1"><Clock size={14} /> Duration</div>
          <p className="text-[18px] font-bold text-white">{Math.floor(view.duration / 60)}m {view.duration % 60}s</p>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-clipz-text-muted mb-1"><Film size={14} /> Resolution</div>
          <p className="text-[18px] font-bold text-white">{view.resolution}</p>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-clipz-text-muted mb-1"><Activity size={14} /> FPS</div>
          <p className="text-[18px] font-bold text-white">{view.fps}</p>
        </div>
        <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
          <div className="flex items-center gap-2 text-[11px] text-clipz-text-muted mb-1"><BarChart3 size={14} /> Status</div>
          <p className="text-[18px] font-bold text-white capitalize">{view.status.replace("_", " ")}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center gap-2 p-4 border-b border-clipz-border-soft">
            <FileText size={14} className="text-clipz-accent-soft" />
            <h3 className="text-[13px] font-semibold text-white">Transcript</h3>
          </div>
          {transcripts ? (
            <div className="p-4 max-h-56 overflow-y-auto">
              <p className="text-[11px] text-clipz-text-muted leading-relaxed">{transcripts.fullText}</p>
              <p className="text-[10px] text-clipz-text-dim mt-2">Confidence: {(transcripts.confidence * 100).toFixed(0)}% · Engine: {transcripts.engine}</p>
            </div>
          ) : (
            <div className="p-8 text-center text-[12px] text-clipz-text-dim">
              <p>No transcript available</p>
            </div>
          )}
        </div>

        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center gap-2 p-4 border-b border-clipz-border-soft">
            <Activity size={14} className="text-clipz-accent-soft" />
            <h3 className="text-[13px] font-semibold text-white">Scenes ({scenes.length})</h3>
          </div>
          <div className="divide-y divide-clipz-border-soft max-h-56 overflow-y-auto">
            {scenes.length > 0 ? scenes.map((s: any, i: number) => (
              <div key={s.id} className="flex items-center justify-between px-4 py-2">
                <span className="text-[11px] text-clipz-text-muted">Scene {i + 1}</span>
                <div className="flex items-center gap-3 text-[10px] text-clipz-text-dim">
                  <span>{Math.floor(s.startMs / 1000 / 60)}m</span>
                  <span>Motion: {(s.motionScore * 100).toFixed(0)}%</span>
                  {s.faceCount > 0 && <span>{s.faceCount} face(s)</span>}
                </div>
              </div>
            )) : (
              <div className="p-4 text-center text-[12px] text-clipz-text-dim">
                <p>No scenes detected</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {candidates.length > 0 && (
        <div className="rounded-xl border border-clipz-border bg-clipz-panel overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
            <h3 className="text-[13px] font-semibold text-white">Candidates ({candidates.length})</h3>
            <Link to="/clip-lab" className="text-[11px] text-clipz-accent-soft hover:text-white">View in Clip Lab</Link>
          </div>
          <div className="divide-y divide-clipz-border-soft">
            {candidates.map((c: any) => (
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
                <span className="text-[11px] font-bold text-clipz-accent-soft">{c.overallScore}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}